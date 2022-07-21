{
module Lex where
}

%wrapper "basic"

$digit = 0-9
$alpha = [a-zA-Z]

tokens :-

  $white                                       ;
  let                                              { \s -> TLet }
  in                                               { \s -> TIn }
  $digit+                                     { \s -> TNum (read s)}
  [\=\+\-\*\/\(\)]                          { \s -> TSym (head s)}
  $alpha [$alpha $digit \_ \']*  { \s -> TVar s}

{
data Token = TLet | TIn | TNum Int | TSym Char | TVar String deriving (Eq, Show)
}