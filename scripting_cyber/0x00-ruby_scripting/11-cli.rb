#!/usr/bin/env ruby

require 'optparse'

TASKS_FILE = 'tasks.txt'

# load_tasks - reads the list of tasks from the tasks file
#
# Return: an array of task strings
def load_tasks
  File.exist?(TASKS_FILE) ? File.readlines(TASKS_FILE).map(&:chomp) : []
end

# save_tasks - writes the list of tasks back to the tasks file
# @tasks: array of task strings to persist
def save_tasks(tasks)
  File.write(TASKS_FILE, tasks.map { |task| "#{task}\n" }.join)
end

options = {}

parser = OptionParser.new do |opts|
  opts.banner = 'Usage: cli.rb [options]'

  opts.on('-a', '--add TASK', 'Add a new task') do |task|
    options[:add] = task
  end

  opts.on('-l', '--list', 'List all tasks') do
    options[:list] = true
  end

  opts.on('-r', '--remove INDEX', Integer, 'Remove a task by index') do |index|
    options[:remove] = index
  end

  opts.on('-h', '--help', 'Show help') do
    puts opts
    exit
  end
end

parser.parse!

tasks = load_tasks

if options[:add]
  tasks << options[:add]
  save_tasks(tasks)
  puts "Task '#{options[:add]}' added."
elsif options[:list]
  puts 'Tasks:'
  tasks.each_with_index { |task, index| puts "#{index + 1}. #{task}" }
elsif options[:remove]
  index = options[:remove] - 1
  if index >= 0 && index < tasks.length
    removed = tasks.delete_at(index)
    save_tasks(tasks)
    puts "Task '#{removed}' removed."
  else
    puts 'Invalid task index.'
  end
else
  puts parser
end
