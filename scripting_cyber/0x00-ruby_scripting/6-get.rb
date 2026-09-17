#!/usr/bin/env ruby

require 'net/http'
require 'uri'
require 'json'

# get_request - performs an HTTP GET request to the given url and
# prints the response status code and the response body formatted
# as JSON
# @url: the url to send the GET request to
def get_request(url)
  uri = URI.parse(url)
  response = Net::HTTP.get_response(uri)

  puts "Response status: #{response.code} #{response.message}"
  puts 'Response body:'
  puts JSON.pretty_generate(JSON.parse(response.body))
end
