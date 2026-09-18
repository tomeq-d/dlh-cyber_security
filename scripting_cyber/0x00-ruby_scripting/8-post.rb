#!/usr/bin/env ruby

require 'net/http'
require 'uri'
require 'json'

# post_request - performs an HTTP POST request to the given url with
# the given body parameters and prints the response status code and
# the response body formatted as JSON
# @url: the url to send the POST request to
# @body_params: hash of parameters to send as the JSON request body
def post_request(url, body_params)
  uri = URI.parse(url)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = uri.scheme == 'https'

  request = Net::HTTP::Post.new(uri.request_uri)
  request['Content-Type'] = 'application/json'
  request.body = body_params.to_json

  response = http.request(request)

  puts "Response status: #{response.code} #{response.message}"
  puts 'Response body:'
  parsed_body = JSON.parse(response.body)
  if parsed_body.respond_to?(:empty?) && parsed_body.empty?
    puts parsed_body.to_json
  else
    puts JSON.pretty_generate(parsed_body)
  end
end
