/**
 * collective.cover - Galleria Theme 2013-02-18
 * http://galleria.io
 *
 * Licensed under the MIT license
 * https://raw.github.com/aino/galleria/master/LICENSE
 *
 */

(function($) {

  /*global jQuery, Galleria */

  Galleria.addTheme({
    name: 'carrossel_theme',
    author: 'Metodista',
    css: '++resource++metodista.site.tiles/css/galleria.carrossel_theme.css',
    defaults: {
      transition: 'slide',
      transition_speed: 500,
      thumbCrop: 'height',
      thumbnails: 'empty',
      carousel: false,
      image_crop: false,
      autoplay: true,
      _toggleInfo: false
    },
    init: function(options) {

      Galleria.requires(1.28, 'This version of Classic theme requires Galleria 1.2.8 or later');

      // cache some stuff
      var touch = Galleria.TOUCH,
        click = touch ? 'touchstart' : 'click';

      // show loader & counter with opacity
      this.$('loader,counter').show().css('opacity', 0.4);

      // some stuff for non-touch browsers
      if (!touch) {
        this.addIdleState(this.get('image-nav-left'), {
          left: -50
        });
        this.addIdleState(this.get('image-nav-right'), {
          right: -50
        });
        this.addIdleState(this.get('counter'), {
          opacity: 0
        });
      }

      this.bind('loadstart', function(e) {
        if (!e.cached) {
          this.$('loader').show().fadeTo(200, 0.4);
        }

        $(e.thumbTarget).css('opacity', 1).parent().siblings().children().css('opacity', 0.6);
      });

      this.bind('loadfinish', function(e) {
        this.$('loader').fadeOut(200);
        var $original = $(e.galleriaData.original);
        var $target = $(this._target);
        $target.attr('data-tile-id', $target.parents('.tile').attr('id'));
        $target.attr('data-tile-type', $target.parents('.tile').attr('data-tile-type'));
        $target.attr('data-content-type', $original.attr('data-content-type'));
        $target.attr('data-content-uuid', $original.attr('data-content-uuid'));
        $target.attr('data-has-subitem', $original.attr('data-has-subitem'));
      });
    }
  });

}(jQuery));