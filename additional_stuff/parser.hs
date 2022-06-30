{-# LANGUAGE LambdaCase #-}

-- module Parsing where

import Control.Applicative ((<|>))
import Control.Monad (liftM, liftM2)
import Data.Complex
import qualified Data.Map as M
import qualified Text.ParserCombinators.Parsec as P
import qualified Text.ParserCombinators.Parsec.Expr as P
import GHC.Base (VecElem(Int16ElemRep))
import Data.Map (valid)
import Data.Maybe (fromMaybe)


import Foreign.C.Types
import Foreign.C.String


-- | Mathematical expressions.
data Expr a
  = Num a
  | Var String
  | Neg (Expr a)
  | Add (Expr a) (Expr a)
  | Sub (Expr a) (Expr a)
  | Mul (Expr a) (Expr a)
  | Div (Expr a) (Expr a)
  | Pow (Expr a) (Expr a)
  | Sqrt (Expr a)
  | Exp (Expr a)
  | Log (Expr a)
  | Abs (Expr a)
  | Sin (Expr a)
  | Cos (Expr a)
  | Tan (Expr a)
  deriving (Show)

-- | Parse a mathematical expression.
--
-- >>> parse "exp(-pi*i)+1"
-- Right (Add (Exp (Mul (Neg (Var "pi")) (Var "i"))) (Num 1.0))
parse :: Floating a => String -> Either P.ParseError (Expr a)
parse = P.parse build "" . (:) '(' . flip (++) ")" . filter (/= ' ')

build :: Floating a => P.Parser (Expr a)
build = P.buildExpressionParser table factor

table :: Floating a => [[P.Operator Char st (Expr a)]]
table =
  [ [prefix "sin" Sin]
  , [prefix "cos" Cos]
  , [prefix "tan" Tan]
  , [prefix "abs" Abs]
  , [prefix "exp" Exp]
  , [prefix "sqrt" Sqrt]
  , [prefix "log" Log]
  , [binary "^" Pow P.AssocRight]
  , [prefix "-" Neg]
  , [binary "*" Mul P.AssocLeft, binary "/" Div P.AssocLeft]
  , [binary "+" Add P.AssocLeft, binary "-" Sub P.AssocLeft]
  ]
  where
    binary s f a = P.Infix (P.string s >> return f) a
    prefix s f = P.Prefix (P.try (P.string s) >> return f)

factor :: Floating a => P.Parser (Expr a)
factor =
  do _ <- P.char '('
     expr <- build
     _ <- P.char ')'
     return $! expr
     <|> variable

variable :: Floating a => P.Parser (Expr a)
variable =
  do var <- P.many1 P.letter
     return $! Var var
     <|> number

number :: Floating a => P.Parser (Expr a)
number = do
  pr <- P.many1 P.digit
  let n = foldl stl 0 pr
  P.option (Num n) . P.try $ do
    _ <- P.char '.'
    su <- P.many1 P.digit
    return $! Num $ n + foldr str 0 su
  where
    stl a x = ctn x - ctn '0' + a * 10
    str x a = (ctn x - ctn '0' + a) / 10
    ctn = realToFrac . fromEnum

-- | Evaluate a mathematical expression
--   using the supplied variable definitions.
--
-- > >>> :m + Data.Complex Data.Map
-- > >>> let def = fromList [("pi", pi), ("i", 0 :+ 1)]
-- > >>> evaluate def . Just $ Add (Exp (Mul (Neg (Var "pi")) (Var "i"))) (Num 1.0)
-- > Just (0.0 :+ (-1.2246467991473532e-16))
--
evaluate ::
     Floating a
  => M.Map String a -- ^ Variable definitions.
  -> Maybe (Expr a) -- ^ Mathematical expression.
  -> Maybe a
evaluate def =
  \case
    Just (Num num) -> Just num
    Just (Var var) -> M.lookup var def
    Just (Neg e1) -> fmap negate (evaluate def $ Just e1)
    Just (Add e1 e2) ->
      liftM2 (+) (evaluate def $ Just e1) (evaluate def $ Just e2)
    Just (Sub e1 e2) ->
      liftM2 (-) (evaluate def $ Just e1) (evaluate def $ Just e2)
    Just (Mul e1 e2) ->
      liftM2 (*) (evaluate def $ Just e1) (evaluate def $ Just e2)
    Just (Div e1 e2) ->
      liftM2 (/) (evaluate def $ Just e1) (evaluate def $ Just e2)
    Just (Pow e1 e2) ->
      liftM2 (**) (evaluate def $ Just e1) (evaluate def $ Just e2)
    Just (Sqrt e1) -> fmap (** 0.5) (evaluate def $ Just e1)
    Just (Exp e1) -> fmap exp (evaluate def $ Just e1)
    Just (Log e1) -> fmap log (evaluate def $ Just e1)
    Just (Abs e1) -> fmap abs (evaluate def $ Just e1)
    Just (Sin e1) -> fmap sin (evaluate def $ Just e1)
    Just (Cos e1) -> fmap cos (evaluate def $ Just e1)
    Just (Tan e1) -> fmap tan (evaluate def $ Just e1)
    _ -> Nothing
  where
    inv = (/) 1


exec :: Floating a => Either P.ParseError (Expr a) -> Maybe (Expr a)
exec expression = case expression of
  (Right val) -> Just val
  (Left err) -> error (show err)


main = do
  expression <- getLine
  let maybeExpr = exec $ parse expression
  let d = M.empty :: M.Map String a
  let maybeResult =  evaluate d maybeExpr
  case maybeResult of
    (Just value) -> if value == 1/0 then error "useless line\nДеление на 0" else print value
    Nothing -> error "useless line\nНеправильное выражение"
