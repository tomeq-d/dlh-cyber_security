#!/usr/bin/env ruby

require 'prime'

# prime - checks whether a given number is a prime number
# @number: the integer to check
#
# Return: true if the number is prime, false otherwise
def prime(number)
  Prime.prime?(number)
end
