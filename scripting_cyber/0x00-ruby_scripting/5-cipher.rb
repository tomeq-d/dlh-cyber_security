#!/usr/bin/env ruby

# CaesarCipher - encrypts and decrypts messages using the
# Caesar cipher technique
class CaesarCipher
  def initialize(shift)
    @shift = shift
  end

  def encrypt(message)
    cipher(message, @shift)
  end

  def decrypt(message)
    cipher(message, -@shift)
  end

  private

  def cipher(message, shift)
    message.chars.map do |char|
      if char =~ /[A-Z]/
        shift_char(char, shift, 'A')
      elsif char =~ /[a-z]/
        shift_char(char, shift, 'a')
      else
        char
      end
    end.join
  end

  def shift_char(char, shift, base)
    offset = char.ord - base.ord
    new_offset = (offset + shift) % 26
    (base.ord + new_offset).chr
  end
end
