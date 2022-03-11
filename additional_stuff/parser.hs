module Main where
import           Control.Exception
import           Data.Char                      ( isNumber )

firstOrderOperations :: [Char]
firstOrderOperations = ['/', '*']
secondOrderOperations :: [Char]
secondOrderOperations = ['-', '+']

strToRPN :: String -> [String] -> [String] -> [String]
strToRPN xss stack out
  | null xss = out ++ stack
  | x == '(' = strToRPN xs ("(" : stack) out
  | x == ')' && null afterBracket = error "parsing poshel po pizde"
  | x == ')' = strToRPN xs (tail afterBracket) (out ++ beforeBracket)
  | x == ' ' = strToRPN xs stack out
  | x `elem` firstOrderOperations = strToRPN xs
                                             ([x] : afterNotFirstPriority)
                                             (out ++ whileFirstPriority)
  | x `elem` secondOrderOperations = strToRPN xs
                                              ([x] : afterBracket)
                                              (out ++ beforeBracket)
  | isNumber x = strToRPN afterNumber stack (out ++ [number])
  | otherwise = error "parse error"
 where
  beforeBracket = takeWhile (/= "(") stack
  afterBracket  = dropWhile (/= "(") stack
  whileFirstPriority =
    takeWhile (\y -> head y `elem` firstOrderOperations) stack
  afterNotFirstPriority =
    dropWhile (\y -> head y `elem` firstOrderOperations) stack
  number      = takeWhile (\y -> isNumber y || y == '.') xss
  afterNumber = dropWhile (\y -> isNumber y || y == '.') xss
  x           = head xss
  xs          = tail xss

rpn :: String -> [String]
rpn str = strToRPN str [] []

transform :: [String] -> String
transform (elem : list) = elem ++ " " ++ transform list
transform []            = ""

solveRPN :: String -> [Double]
solveRPN = foldl foldingFunction [] . words
 where
  foldingFunction (x : y : ys) "*"          = (x * y) : ys
  foldingFunction (x : y : ys) "+"          = (x + y) : ys
  foldingFunction (x : y : ys) "-"          = (y - x) : ys
  foldingFunction (x     : xs) "-"          = -x : xs
  foldingFunction xs           numberString = read numberString : xs



main = do
  str <- getLine
  let result = solveRPN $ transform $ rpn str
  if length result > 1 
    then print "dolbaeb" 
    else print $ head result

