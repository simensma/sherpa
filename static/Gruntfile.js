'use strict';

try {
  var LIVERELOAD_PORT = 35729;
  var lrSnippet = require('connect-livereload')({port: LIVERELOAD_PORT});
  var mountFolder = function (dir) {
    return require('serve-static')(require('path').resolve(dir));
  };
} catch (e) { }

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {
  // show elapsed time at the end
  require('time-grunt')(grunt);

  // configurable paths
  var yeomanConfig = {
    polymer: {
      src: 'polymer/src',
      dist: 'polymer/dist'
    },
    less: {
      src: 'less',
      dist: 'css'
    }
  };

  grunt.initConfig({
    yeoman: yeomanConfig,
    watch: {
      options: {
        nospawn: true,
        livereload: { liveCSS: false }
      },
      livereload: {
        options: {
          livereload: true
        },
        files: [
          '<%= yeoman.polymer.src %>/*.html',
          '<%= yeoman.polymer.src %>/elements/{,*/}*.html',
          '{.tmp,<%= yeoman.polymer.src %>}/elements/{,*/}*.css',
          '{.tmp,<%= yeoman.polymer.src %>}/styles/{,*/}*.css',
          '{.tmp,<%= yeoman.polymer.src %>}/scripts/{,*/}*.js',
          '<%= yeoman.polymer.src %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
        ]
      },
      html: {
        files: ['<%= yeoman.polymer.src %>/elements/{,*/}*.html'],
        tasks: ['copy:dist']
      },
      js: {
        files: ['<%= yeoman.polymer.src %>/scripts/{,*/}*.js'],
        tasks: ['jshint', 'copy:dist']
      },
      styles: {
        files: [
          '<%= yeoman.polymer.src %>/styles/{,*/}*.css',
          '<%= yeoman.polymer.src %>/elements/{,*/}*.css'
        ],
        tasks: ['copy:styles', 'autoprefixer:server']
      },
      sass: {
        files: [
          '<%= yeoman.polymer.src %>/styles/{,*/}*.{scss,sass}',
          '<%= yeoman.polymer.src %>/elements/{,*/}*.{scss,sass}'
        ],
        tasks: ['sass:server', 'autoprefixer:server']
      },
      less: {
        files: ['less/**/*.less'],
        tasks: ['recess'],
        options: {
          nospawn: true
        }
      }
    },
    // Compiles Sass to CSS and generates necessary files if requested
    sass: {
      options: {
        loadPath: 'bower_components'
      },
      dist: {
        options: {
          style: 'compressed'
        },
        files: [{
          expand: true,
          cwd: '<%= yeoman.polymer.src %>',
          src: ['styles/{,*/}*.{scss,sass}', 'elements/{,*/}*.{scss,sass}'],
          dest: '<%= yeoman.polymer.dist %>',
          ext: '.css'
        }]
      },
      server: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.polymer.src %>',
          src: ['styles/{,*/}*.{scss,sass}', 'elements/{,*/}*.{scss,sass}'],
          dest: '.tmp',
          ext: '.css'
        }]
      }
    },
    recess: {
      dist: {
        options: {
          compile: true
        },
        files:[{
          expand: true,
          cwd: '<%= yeoman.less.src %>/',
          src: '*.less',
          dest: '<%= yeoman.less.dist %>/',
          ext: '.css'
        }]
      }
    },
    autoprefixer: {
      options: {
        browsers: ['last 2 versions']
      },
      server: {
        files: [{
          expand: true,
          cwd: '.tmp',
          src: '**/*.css',
          dest: '.tmp'
        }]
      },
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.polymer.dist %>',
          src: ['**/*.css', '!bower_components/**/*.css'],
          dest: '<%= yeoman.polymer.dist %>'
        }]
      }
    },
    connect: {
      options: {
        port: 9000,
        // change this to '0.0.0.0' to access the server from outside
        hostname: 'localhost'
      },
      livereload: {
        options: {
          middleware: function () {
            return [
              lrSnippet,
              mountFolder('.tmp'),
              mountFolder(yeomanConfig.polymer.src)
            ];
          }
        }
      },
      test: {
        options: {
          open: {
            target: 'http://localhost:<%= connect.options.port %>/test'
          },
          middleware: function () {
            return [
              mountFolder('.tmp'),
              mountFolder(yeomanConfig.polymer.src)
            ];
          },
          keepalive: true
        }
      },
      dist: {
        options: {
          middleware: function () {
            return [
              mountFolder(yeomanConfig.polymer.dist)
            ];
          }
        }
      }
    },
    open: {
      server: {
        path: 'http://localhost:<%= connect.options.port %>'
      }
    },
    clean: {
      dist: ['.tmp', '<%= yeoman.polymer.dist %>/*'],
      server: '.tmp'
    },
    jshint: {
      options: {
        jshintrc: '.jshintrc',
        reporter: require('jshint-stylish')
      },
      all: [
        '<%= yeoman.polymer.src %>/scripts/{,*/}*.js',
        '!<%= yeoman.polymer.src %>/scripts/vendor/*',
        'test/spec/{,*/}*.js'
      ]
    },
    useminPrepare: {
      html: '<%= yeoman.polymer.src %>/index.html',
      options: {
        dest: '<%= yeoman.polymer.dist %>'
      }
    },
    usemin: {
      html: ['<%= yeoman.polymer.dist %>/{,*/}*.html'],
      css: ['<%= yeoman.polymer.dist %>/styles/{,*/}*.css'],
      options: {
        dirs: ['<%= yeoman.polymer.dist %>'],
        blockReplacements: {
          vulcanized: function (block) {
            return '<link rel="import" href="' + block.dest + '">';
          }
        }
      }
    },
    vulcanize: {
      default: {
        options: {
          strip: true,
          inline: true
        },
        files: {
          '<%= yeoman.polymer.dist %>/elements/elements.vulcanized.html': [
            '<%= yeoman.polymer.dist %>/elements/elements.html'
          ]
        }
      }
    },
    imagemin: {
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.polymer.src %>/images',
          src: '{,*/}*.{png,jpg,jpeg,svg}',
          dest: '<%= yeoman.polymer.dist %>/images'
        }]
      }
    },
    minifyHtml: {
      options: {
        quotes: true,
        empty: true,
        spare: true
      },
      app: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.polymer.dist %>',
          src: '*.html',
          dest: '<%= yeoman.polymer.dist %>'
        }]
      }
    },
    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.polymer.src %>',
          dest: '<%= yeoman.polymer.dist %>',
          src: [
            '*.{ico,txt}',
            '.htaccess',
            '*.html',
            'elements/**',
            '!elements/**/*.scss',
            'images/{,*/}*.{webp,gif}',
            'bower_components/**'
          ]
        }]
      },
      styles: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.polymer.src %>',
          dest: '.tmp',
          src: ['{styles,elements}/{,*/}*.css']
        }]
      }
    },
    'wct-test': {
      options: {
        root: '<%= yeoman.polymer.src %>',
        plugins: {
          serveStatic: {
            middleware: function() {
              return mountFolder('.tmp');
            }
          }
        }
      },
      local: {
        options: {remote: false}
      },
      remote: {
        options: {remote: true}
      }
    },
    // See this tutorial if you'd like to run PageSpeed
    // against localhost: http://www.jamescryer.com/2014/06/12/grunt-pagespeed-and-ngrok-locally-testing/
    pagespeed: {
      options: {
        // By default, we use the PageSpeed Insights
        // free (no API key) tier. You can use a Google
        // Developer API key if you have one. See
        // http://goo.gl/RkN0vE for info
        nokey: true
      },
      // Update `url` below to the public URL for your site
      mobile: {
        options: {
          url: "https://developers.google.com/web/fundamentals/",
          locale: "en_GB",
          strategy: "mobile",
          threshold: 80
        }
      }
    }
  });

  // Load all required Grunt plugins
  grunt.loadNpmTasks('grunt-autoprefixer');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-minify-html');
  grunt.loadNpmTasks('grunt-pagespeed');
  grunt.loadNpmTasks('grunt-recess');
  grunt.loadNpmTasks('grunt-rev');
  grunt.loadNpmTasks('grunt-usemin');
  grunt.loadNpmTasks('grunt-vulcanize');

  // Only load imagemin if it is installed
  try {
    require.resolve('grunt-contrib-imagemin');
    grunt.loadNpmTasks('grunt-contrib-imagemin');
  } catch (e) {}

  // Only load wtc if it is installed
  try {
    require.resolve('web-componenttester');
    grunt.loadNpmTasks('web-componenttester');
  } catch (e) {}

  // Register Grunt tasks
  grunt.registerTask('default', ['jshint', 'build', 'watch']);
  grunt.registerTask('build', [
    'clean:dist',
    'sass',
    'copy',
    'useminPrepare',
    // 'imagemin', <= This should be done before commit
    // 'concat',
    'autoprefixer',
    // 'uglify',
    'vulcanize',
    // 'usemin',
    'minifyHtml'
  ]);

  grunt.registerTask('server', function (target) {
    grunt.log.warn('The `server` task has been deprecated. Use `grunt serve` to start a server.');
    grunt.task.run(['serve:' + target]);
  });

  grunt.registerTask('serve', function (target) {
    if (target === 'dist') {
      return grunt.task.run(['build', 'open', 'connect:dist:keepalive']);
    }

    grunt.task.run([
      'clean:server',
      'sass:server',
      'copy:styles',
      'autoprefixer:server',
      'connect:livereload',
      'open',
      'watch'
    ]);
  });

  grunt.registerTask('test', ['wct-test:local']);
  grunt.registerTask('test:browser', ['connect:test']);
  grunt.registerTask('test:remote', ['wct-test:remote']);
};

