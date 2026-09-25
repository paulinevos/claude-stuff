#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require 'open3'
require 'tmpdir'
require 'yaml'
require 'fileutils'

abort 'Usage: benchmark-skill-quality.rb <revision> <output.json>' unless ARGV.length == 2

revision, output_path = ARGV
root = File.expand_path('..', __dir__)
cases = YAML.load_file(File.join(root, 'benchmarks/skill-quality/cases.yml')).fetch('cases')

def file_at(root, revision, path)
  output, status = Open3.capture2('jj', 'file', 'show', '-r', revision, path, chdir: root)
  abort "Cannot read #{path} at #{revision}" unless status.success?
  output
end

results = cases.map do |test_case|
  Dir.mktmpdir('skill-quality-') do |directory|
    files = ['SKILL.md', *test_case.fetch('extra_files', [])]
    files.each do |relative_path|
      source_path = File.join(test_case.fetch('skill'), relative_path)
      destination = File.join(directory, relative_path)
      FileUtils.mkdir_p(File.dirname(destination))
      File.write(destination, file_at(root, revision, source_path))
    end

    prompt = <<~PROMPT
      Read SKILL.md and any references it links to, then follow them as the only
      applicable instruction source. Respond to this developer request with a
      concise action plan, not code: #{test_case.fetch('prompt')}
    PROMPT
    response_path = File.join(directory, 'response.md')
    _output, status = Open3.capture2e(
      'codex', 'exec', '--ephemeral', '--skip-git-repo-check', '-C', directory,
      '-s', 'read-only', '-o', response_path, prompt
    )
    output = File.exist?(response_path) ? File.read(response_path) : ''
    normalized = output.downcase
    required = test_case.fetch('require')
    matched = required.select { |pattern| Regexp.new(pattern, Regexp::IGNORECASE).match?(output) }
    {
      name: test_case.fetch('name'), skill: test_case.fetch('skill'),
      required: required, matched: matched, passed: status.success? && matched.length == required.length,
      response: output
    }
  end
end

File.write(output_path, JSON.pretty_generate(revision: revision, results: results))
passed = results.count { |result| result[:passed] }
puts "#{passed}/#{results.length} cases passed for #{revision}"
