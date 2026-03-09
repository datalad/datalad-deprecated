module.exports = function(grunt) {
  // Project configuration.
  grunt.initConfig({
    qunit: {
      options: {
        puppeteer: {
          headless: 'new',
          args: process.env.CI ? ['--no-sandbox'] : []
        }
      },
      files: ['datalad_deprecated/resources/website/tests/test.html']
    }
  });
  // Load plugin
  grunt.loadNpmTasks('grunt-contrib-qunit');
  // Task to run tests
  grunt.registerTask('test', 'qunit');
};
