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
    | x == ')' =                       strToRPN xs (tail afterBracket) (out ++ beforeBracket)
    | x == ' ' =                       strToRPN xs stack out
    | x `elem` firstOrderOperations =  strToRPN xs ([x] : afterNotFirstPriority) (out ++ whileFirstPriority)
    | x `elem` secondOrderOperations = strToRPN xs ([x] : afterBracket) (out ++ beforeBracket)
    | x `elem` digits =               strToRPN afterNumber stack (out ++ [number])
    | otherwise = error "parse error"
    where   beforeBracket =          takeWhile (/= "(") stack
            afterBracket =           dropWhile (/= "(") stack
            whileFirstPriority =     takeWhile (\x -> head x `elem` firstOrderOperations) stack
            afterNotFirstPriority =  dropWhile (\x -> head x `elem` firstOrderOperations) stack
            number =                 takeWhile (`elem` digits) xss
            afterNumber =            dropWhile (`elem` digits) xss
            x =                      head xss
            xs =                     tail xss

test :: String -> [String]
test str = strToRPN str [] []

eval :: [String] -> [String] -> Int
eval before next
    | null next && length before == 1 = read $ head before :: Int
    | null (tail next) && not (all isDigit (head next)) = error "eblan?"
    | head next == "+" =                eval (newBefore ++ [show $ first + second]) (tail next)
    | head next == "-" =                eval (newBefore ++ [show $ first - second]) (tail next)
    | head next == "*" =                eval (newBefore ++ [show $ first * second]) (tail next)
    | head next == "/" =                eval (newBefore ++ [show $ first `div` second]) (tail next)
    | all isDigit (head next) =         eval (before ++ [head next]) (tail next)
    | otherwise =                       error "ti eblan vashe?"
    where second =     read $ last before :: Int
          first =      read $ head $ tail (reverse before) :: Int
          newBefore =  reverse(tail $ tail (reverse before))

compute :: String -> Int
compute string = eval [] (test string)

main :: IO ()
main = do
    str <- getLine
    print $ compute str
