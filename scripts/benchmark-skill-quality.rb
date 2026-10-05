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

# A settings file blanking the model-routing variables. Without it the runner
# inherits whatever gateway the operator's settings point at — on a machine
# routing Claude Code through a third-party gateway, every case silently runs
# on another vendor's model and the scores describe that model, not the skill.
def neutral_settings
  path = File.join(Dir.tmpdir, 'skill-quality-settings.json')
  blanked = %w[
    ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_CUSTOM_HEADERS
    ANTHROPIC_MODEL ANTHROPIC_SMALL_FAST_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL
    ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL
  ].to_h { |name| [name, ''] }
  File.write(path, JSON.generate(env: blanked))
  path
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

    # The claude runner gets the skill text inlined instead of a directory to
    # read, so every tool can be denied. Reading a file is the one capability
    # a case needs, and leaving it open is what let earlier runs wander into
    # the operator's real repositories and configuration.
    inlined = files.map do |relative_path|
      "===== #{relative_path} =====\n#{File.read(File.join(directory, relative_path))}"
    end.join("\n\n")
    inline_prompt = <<~PROMPT
      The following files are the only applicable instruction source. Follow
      them. Answer from them alone: you have no tools, so do not attempt to
      read, search or run anything, and do not ask for access.

      #{inlined}

      ===== request =====
      Respond to this developer request with a concise action plan, not code:
      #{test_case.fetch('prompt')}
    PROMPT
    response_path = File.join(directory, 'response.md')
    runner = ENV.fetch('BENCHMARK_RUNNER', 'codex')
    stdout, status =
      case runner
      when 'codex'
        Open3.capture2e(
          'codex', 'exec', '--ephemeral', '--skip-git-repo-check', '-C', directory,
          '-s', 'read-only', '-o', response_path, prompt, chdir: directory
        )
      when 'claude'
        # The prompt goes on stdin: as an argument it is swallowed by the
        # variadic flag preceding it. The settings and MCP flags keep the run
        # off the operator's plugins, servers and permissions, so a case
        # measures the skill rather than the machine it runs on. The config
        # directory cannot be redirected as well: the credentials live there,
        # and a run without them only answers "Not logged in".
        # The model is pinned so a score means the same thing on every machine.
        Open3.capture2e(
          'claude', '-p', '--permission-mode', 'plan', '--strict-mcp-config',
          '--setting-sources', '', '--settings', neutral_settings,
          '--disable-slash-commands',
          '--disallowed-tools', 'Bash', 'Edit', 'Write', 'Read', 'Glob', 'Grep',
          'WebFetch', 'WebSearch', 'NotebookEdit', 'Agent', 'Task', 'ExitPlanMode',
          '--model', ENV.fetch('BENCHMARK_MODEL', 'sonnet'),
          chdir: directory, stdin_data: inline_prompt
        )
      else
        abort "Unknown BENCHMARK_RUNNER #{runner}; use codex or claude"
      end
    File.write(response_path, stdout) if runner == 'claude'
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
