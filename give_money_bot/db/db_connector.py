import datetime
import typing
from typing import Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from give_money_bot.db.models import Credit, ShowTypes, User, UserVision


def add_entry(
    session: Session,
    to_user: int,
    from_users: List[int],
    amount: int,
    additional_info: str = "",
) -> None:
    for from_user in from_users:
        session.add(
            Credit(
                to_id=to_user,
                from_id=from_user,
                amount=amount,
                text_info=additional_info,
                discount=0,
            )
        )
    session.commit()


def add_entry_2(
    session: Session,
    to_users: List[int],
    from_user: int,
    amount: int,
    additional_info: str = "",
) -> None:
    for to_user in to_users:
        session.add(
            Credit(
                to_id=to_user,
                from_id=from_user,
                amount=amount,
                text_info=additional_info,
                discount=0,
            )
        )
    session.commit()


def get_user_credits(session: Session, user: int) -> List[Credit]:
    return (
        session.query(Credit)
        .filter(Credit.from_id == user)
        .filter(Credit.returned == False)
        .order_by(Credit.to_id)
        .order_by(Credit.date)
        .all()
    )


def credits_to_user(session: Session, user: int) -> List[Credit]:
    return (
        session.query(Credit)
        .filter(Credit.to_id == user)
        .filter(Credit.returned == False)
        .order_by(Credit.from_id)
        .order_by(Credit.date)
        .all()
    )


def get_credits_to_user_from_user(session: Session, from_user: int, to_user: int) -> List[Credit]:
    return (
        session.query(Credit)
        .filter(Credit.to_id == to_user)
        .filter(Credit.from_id == from_user)
        .filter(Credit.returned == False)
        .all()
    )


def return_credits(session: Session, credit_ids: typing.Union[List[int], int, Credit]) -> None:
    if isinstance(credit_ids, int):
        credit_ids = [credit_ids]
    if isinstance(credit_ids, Credit):
        credit_ids = [credit_ids.id]

    for credit_id in credit_ids:
        credit: Credit = session.query(Credit).filter(Credit.id == credit_id).first()
        credit.returned = True
        credit.return_date = datetime.datetime.utcnow()
    session.commit()


def get_credit(session: Session, credit_id: int) -> Credit:
    return session.query(Credit).filter(Credit.id == credit_id).first()


def get_credits(session: Session) -> List[Credit]:
    return session.query(Credit).filter(Credit.returned == False).all()


def add_discount(session: Session, credit: typing.Union[int, Credit], discount: int) -> None:
    if isinstance(credit, int):
        credit = get_credit(session, credit)
    if credit.discount is None:
        credit.discount = 0
    credit.discount += discount
    session.commit()


def get_user(session: Session, user_id: int) -> User:
    return session.query(User).filter(User.user_id == user_id).first()


def get_users(session: Session, user_ids: Optional[Iterable[int]] = None) -> List[User]:
    if user_ids is None:
        return session.query(User).order_by(User.name.asc()).all()
    return session.query(User).filter(User.user_id.in_(user_ids)).all()


def get_user_ids(session: Session) -> List[int]:
    return [e.user_id for e in get_users(session)]


def get_user_ids_with_name(session: Session) -> Dict[int, str]:
    return {user.user_id: user.name for user in session.query(User).all()}


def get_user_ids_with_users(session: Session) -> Dict[int, User]:
    return {user.user_id: user for user in session.query(User).all()}


def get_admin(session: Session) -> User:
    return session.query(User).filter(User.admin == True).first()


def get_all_users_without_current_user(session: Session, curr_user: int) -> List[User]:
    return session.query(User).filter(User.user_id != curr_user).order_by(User.name.asc()).all()


def get_users_with_show_always(session: Session, user_id: int) -> List[User]:
    resp: List[UserVision] = (
        session.query(UserVision)  # type: ignore
        .filter(UserVision.user_id == user_id)
        .filter(UserVision.show_type == ShowTypes.ALWAYS)
        .join(UserVision.show_user)
        .order_by(User.name.asc())
        .all()
    )
    res = []
    for user_vision in resp:
        res.append(user_vision.show_user)

    return res


def get_users_with_show_more(session: Session, user_id: int) -> List[User]:
    resp: List[UserVision] = (
        session.query(UserVision)  # type: ignore
        .filter(UserVision.user_id == user_id)
        .filter((UserVision.show_type == ShowTypes.ADDITIONAL) | (UserVision.show_type == ShowTypes.ALWAYS))
        .join(UserVision.show_user)
        .order_by(User.name.asc())
        .all()
    )
    res = []
    for user_vision in resp:
        res.append(user_vision.show_user)

    return res


def get_user_visions(session: Session, user_id: int) -> List[UserVision]:
    return session.query(UserVision).filter(UserVision.user_id == user_id).all()


def get_vision(session: Session, user_id: int, show_user_id: int) -> UserVision:
    return (
        session.query(UserVision)
        .filter(UserVision.user_id == user_id)
        .filter(UserVision.show_user_id == show_user_id)
        .first()
    )


def update_user_vision(session: Session, user_id: int, show_user_id: int, show_type: ShowTypes) -> None:
    vision = get_vision(session, user_id, show_user_id)
    if vision is None:
        new_vision = UserVision(user_id=user_id, show_user_id=show_user_id, show_type=show_type)
        session.add(new_vision)
    else:
        vision.show_type = show_type
    session.commit()


def add_user(session: Session, user_id: int, name: str) -> User:
    user = User(user_id=user_id, name=name, admin=False)
    session.add(user)
    session.commit()
    return user


def change_phone(session: Session, user: User, phone: str) -> None:
    user.phone_number = phone
    session.commit()
