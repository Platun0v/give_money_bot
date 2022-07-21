
import qualified Data.Map as M
import Lex
import Synt

newtype Context =
  Context
    { getContext :: M.Map String Int
    }
  deriving (Show)

pull :: Maybe a -> a
pull (Just m) = m
pull Nothing = error "Undefined variable"

createContext :: Context
createContext = Context {getContext = M.empty}

getValue :: Context -> String -> Maybe Int
getValue ctx name = M.lookup name $ getContext ctx

solveExp :: Context -> Exp -> Maybe Int
solveExp ctx exp =
  case exp of
    (Let name expl rexp) -> solveExp newCtx rexp
      where newCtx =
              Context
                { getContext =
                    M.insert name (pull (solveExp ctx expl)) (getContext ctx)
                }
    (Exp1 exp1) -> solveExp1 ctx exp1

solveExp1 :: Context -> Exp1 -> Maybe Int
solveExp1 ctx exp1 =
  case exp1 of
    (Plus lexp1 rterm) -> (+) <$> solveExp1 ctx lexp1 <*> solveTerm ctx rterm
    (Minus lexp1 rterm) -> (-) <$> solveExp1 ctx lexp1 <*> solveTerm ctx rterm
    (Term term) -> solveTerm ctx term
    (Neg term) -> negate <$> solveTerm ctx term

solveTerm :: Context -> Term -> Maybe Int
solveTerm ctx term =
  case term of
    (Mul lterm rfactor) ->
      (*) <$> solveTerm ctx lterm <*> solveFactor ctx rfactor
    (Div lterm rfactor) ->
      div <$> solveTerm ctx lterm <*> solveFactor ctx rfactor
    (Factor factor) -> solveFactor ctx factor

solveFactor :: Context -> Factor -> Maybe Int
solveFactor ctx factor =
  case factor of
    (Num n) -> Just n
    (Var s) -> getValue ctx s
    (Brack exp) -> solveExp ctx exp

main = do
  s <- getLine
  mapM (print . pull . solveExp createContext . synt . alexScanTokens) (lines s)
