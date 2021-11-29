module Main where
import Data.Char

firstOrderOperations :: [Char]
firstOrderOperations = ['/', '*']
secondOrderOperations :: [Char]
secondOrderOperations = ['-', '+']
digits :: [Char]
digits = ['1', '2', '3', '4', '5', '6','7','8','9','0']



strToRPN :: String -> [String] -> [String] -> [String]
strToRPN xss stack out
    | null xss =                       out ++ stack
    | x == '(' =                       strToRPN xs ("(" : stack) out
    | x == ')' && null afterBracket = error "parsing poshel po pizde"
    | x == ')' =                       strToRPN xs (tail afterBracket) (out ++ beforeBracket)
    | x == ' ' =                       strToRPN xs stack out
    | x `elem` firstOrderOperations =  strToRPN xs ([x] : afterNotFirstPriority) (out ++ whileFirstPriority)
    | x `elem` secondOrderOperations = strToRPN xs ([x] : afterBracket) (out ++ beforeBracket)
    | x `elem` digits =               strToRPN afterNumber stack (out ++ [number])
    | otherwise = error "parse error"
    where   beforeBracket =          takeWhile (/= "(") stack
            afterBracket =           dropWhile (/= "(") stack
            whileFirstPriority =     takeWhile (\y -> head y `elem` firstOrderOperations) stack
            afterNotFirstPriority =  dropWhile (\y -> head y `elem` firstOrderOperations) stack
            number =                 takeWhile (\y -> y `elem` digits || y == '.') xss
            afterNumber =            dropWhile (\y -> y `elem` digits || y == '.') xss
            x =                      head xss
            xs =                     tail xss

test :: String -> [String]
test str = strToRPN str [] []

eval :: [String] -> [String] -> Float
eval before next
    | null next && length before == 1 = read $ head before :: Float
    | not (all (\x -> isDigit x || x == '.') $ head next) && length before < 2 = error "eblan?"
    | head next == "+" =                eval (newBefore ++ [show $ first + second]) (tail next)
    | head next == "-" =                eval (newBefore ++ [show $ first - second]) (tail next)
    | head next == "*" =                eval (newBefore ++ [show $ first * second]) (tail next)
    | head next == "/" =                eval (newBefore ++ [show $ first / second]) (tail next)
    | all (\x -> isDigit x || x == '.') (head next) =         eval (before ++ [head next]) (tail next)
    | otherwise =                       error "unexprected eblan"
    where second =     read $ last before :: Float
          first =      read $ head $ tail (reverse before) :: Float
          newBefore =  reverse(tail $ tail (reverse before))

compute :: String -> Int
compute string = round $ eval [] (test string)

main :: IO ()
main = do
    str <- getLine
    print $ compute str
