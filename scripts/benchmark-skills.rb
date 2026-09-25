#!/usr/bin/env ruby
# frozen_string_literal: true

require 'pathname'

root = Pathname.new(__dir__).join('..').realpath
paths = Dir[root.join('plugins/*/skills/*/SKILL.md').to_s].sort

rows = paths.map do |path|
  content = File.read(path)
  relative_path = Pathname.new(path).relative_path_from(root)
  [relative_path, content.lines.count, content.scan(/\S+/).count, content.bytesize]
end

totals = rows.transpose.drop(1).map { |values| values.sum }

puts '| Skill | Lines | Words | Bytes |'
puts '| --- | ---: | ---: | ---: |'
rows.each do |path, lines, words, bytes|
  puts "| `#{path}` | #{lines} | #{words} | #{bytes} |"
end
puts "| **Total** | **#{totals[0]}** | **#{totals[1]}** | **#{totals[2]}** |"
