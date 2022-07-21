{
module Synt where
import Lex
}

%name synt
%tokentype { Token }
%error { parseError }

%token
  let         { TLet }
  in          { TIn }
  num         { TNum $$ }
  var         { TVar $$ }
  '='         { TSym '=' }
  '+'         { TSym '+' }
  '-'         { TSym '-' }
  '*'         { TSym '*' }
  '/'         { TSym '/' }
  '('         { TSym '(' }
  ')'         { TSym ')' }

%%

Exp:
  let var '=' Exp in Exp        { Let $2 $4 $6 }
  | Exp1                        { Exp1 $1 }

Exp1:
  Exp1 '+' Term                 { Plus $1 $3 }
  | '-' Term                    { Neg $2 }
  | Exp1 '-' Term               { Minus $1 $3 }
  | Term                        { Term $1 }

Term:
  Term '*' Factor               { Mul $1 $3 }
  | Term '/' Factor             { Div $1 $3 }
  | Factor                      { Factor $1 }

Factor:
  num                           { Num $1 }
  | var                         { Var $1 }
  | '(' Exp ')'                 { Brack $2 }

{
parseError :: [Token] -> a
parseError _ = error "Parse error"

data Exp = Let String Exp Exp | Exp1 Exp1 deriving (Show)
data Exp1 = Plus Exp1 Term | Minus Exp1 Term | Term Term | Neg Term deriving (Show)
data Term = Mul Term Factor | Div Term Factor | Factor Factor deriving (Show)
data Factor = Num Int | Var String | Brack Exp deriving (Show)
}