from dataclasses import dataclass
from pprint import pprint, pformat
from typing import List, Dict, Optional

from give_money_bot.db.db_connector import db
from give_money_bot.db.models import Credit


class Edge:
    def __init__(self, from_id: int, to_id: int) -> None:
        self.from_id = from_id
        self.to_id = to_id
        self.credits: List[Credit] = []

    @property
    def exist(self) -> bool:
        return bool(len(self.credits))

    @property
    def amount(self) -> int:
        sm = 0
        for credit in self.credits:
            sm += credit.get_amount()
        return sm

    def add_discount(self, discount: int) -> None:
        self.credits.sort(key=lambda x: x.amount)
        for credit in self.credits:
            credit_amount = credit.get_amount()
            if credit_amount <= discount:
                db.add_discount(credit, credit_amount)
                db.return_credits(credit)
                discount -= credit_amount
            else:
                db.add_discount(credit, discount)
                break

    def __repr__(self) -> str:
        return f"<Edge(from_id='{db.get_user(self.from_id).name}', to_id='{db.get_user(self.to_id).name}', amount='{self.amount}')>" if self.exist else ""


class Graph:
    def __init__(self, credits: List[Credit]) -> None:
        # print(credits)
        self.user_ids = db.get_user_ids()
        self.graph: Dict[int, Dict[int, Edge]] = {}
        for id1 in self.user_ids:
            self.graph[id1] = {}
            for id2 in self.user_ids:
                if id1 == id2:
                    continue
                self.graph[id1][id2] = Edge(id1, id2)

        for credit in credits:
            self.graph[credit.from_id][credit.to_id].credits.append(credit)

        self.colors: Dict[int, int] = {}
        self.path: Dict[int, int] = {}
        self.c_start = 0
        self.c_end = 0

    def find_cycle(self) -> Optional[List[Edge]]:
        for user_id in self.user_ids:
            self.colors[user_id] = 0
            self.path[user_id] = -1
        self.c_start = -1

        for user_id in self.user_ids:
            if self.dfs(user_id):
                break
        if self.c_start != -1:
            cycle = [self.graph[self.c_end][self.c_start]]
            while self.c_start != self.c_end:
                next_c = self.path[self.c_start]
                cycle.append(self.graph[self.c_start][next_c])
                self.c_start = next_c
            return cycle
        return None

    def dfs(self, vertex: int) -> bool:
        self.colors[vertex] = 1
        for user_id, edge in self.graph[vertex].items():
            if edge.exist:
                if self.colors[user_id] == 0:
                    self.path[vertex] = user_id
                    if self.dfs(user_id):
                        return True
                if self.colors[user_id] == 1:
                    self.c_start = user_id
                    self.c_end = vertex
                    return True
        self.colors[vertex] = 2
        return False


@dataclass
class SqueezeReport:
    amount: int
    cycle: List[Edge]


def squeeze() -> List[SqueezeReport]:
    report: List[SqueezeReport] = []
    while True:
        g = Graph(db.get_credits())
        # pprint(g.graph)
        c = g.find_cycle()
        if c is None:
            break
        mn_amount = min(c, key=lambda x: x.amount).amount
        # print(mn_amount)
        # pprint(c)
        for edge in c:
            edge.add_discount(mn_amount)
        # pprint(c)
        report.append(SqueezeReport(amount=mn_amount, cycle=c))
    return report
