module Jekyll
  module FileMtimeFilter
    def file_mtime(input)
      return Time.now.xmlschema unless input

      begin
        # Handle both pages and posts
        if input.respond_to?(:path) && input.path
          file_path = input.path
        elsif input.respond_to?(:relative_path) && input.relative_path
          site_source = @context.registers[:site].source
          file_path = File.join(site_source, input.relative_path)
        elsif input.is_a?(Hash) && input['path']
          file_path = input['path']
        else
          return Time.now.xmlschema
        end

        if File.exist?(file_path)
          File.mtime(file_path).xmlschema
        else
          Time.now.xmlschema
        end
      rescue => e
        # Debug: Log error if needed
        # Jekyll.logger.warn "FileMtime Error:", e.message
        Time.now.xmlschema
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::FileMtimeFilter)