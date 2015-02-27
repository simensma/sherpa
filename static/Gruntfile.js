'use strict';
var LIVERELOAD_PORT = 35729;
var lrSnippet = require('connect-livereload')({port: LIVERELOAD_PORT});
var mountFolder = function (dir) {
  console.log('dir', dir, typeof dir);
  return require('serve-static')(require('path').resolve(dir));
};

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {
  // show elapsed time at the end
  require('time-grunt')(grunt);
  // load all grunt tasks
  require('load-grunt-tasks')(grunt);
  grunt.loadNpmTasks('web-component-tester');

  // configurable paths
  var yeomanConfig = {
    polymer: {
      src: 'polymer/src',
      dist: 'polymer/dist'
    },
    less: 'less'
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
      js: {
        files: ['<%= yeoman.polymer.src %>/scripts/{,*/}*.js'],
        tasks: ['jshint']
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
        files: {
          "css/public.css": "less/public.less",
          "css/admin.css": "less/admin.less",
          "css/editor.css": "less/editor.less",
          "css/print.css": "less/print.less",
          "css/500.css": "less/500.less",
          "css/ie7.css": "less/ie7.less"
        }
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

  grunt.registerTask('build', [
    'clean:dist',
    'sass',
    'copy',
    'useminPrepare',
    'imagemin',
    // 'concat',
    'autoprefixer',
    // 'uglify',
    'vulcanize',
    // 'usemin',
    'minifyHtml'
  ]);

  grunt.registerTask('default', [
    'jshint',
    // 'test'
    'build'
  ]);

};