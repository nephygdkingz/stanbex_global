/***************************************************
==================== JS INDEX ======================
****************************************************
01. PreLoader Js
02. Sticky Header Js
03.Header Hight Js
04. Header Class Add Js
05. One Page Scroll Js
06. Common Js
07. Humburger Js
08. Menu Style Js
08. filter
09. Search Js
10. Offcanvas Js
11. Body Overlay Js
12. Nice Select Js
14. Back to Top Js
15. Masonry Js
16. Wow Js
17. Counter Js
****************************************************/

(function ($) {
  "use strict";

  var windowOn = $(window);
  ////////////////////////////////////////////////////
  // 01. PreLoader Js
  windowOn.on("load", function () {
    $("#loading").fadeOut(500);
  });

  ////////////////////////////////////////////////////
  // 02. Sticky Header Js
  windowOn.on("scroll", function () {
    var scroll = $(window).scrollTop();
    if (scroll < 200) {
      $("#header-sticky").removeClass("tp-header-sticky");
    } else {
      $("#header-sticky").addClass("tp-header-sticky");
    }
  });

  ////////////////////////////////////////////////////
  // 03.Header Hight Js
  if ($(".tp-header-height").length > 0) {
    var headerHeight = document.querySelector(".tp-header-height");

    var setHeaderHeight = headerHeight.offsetHeight;

    $(".tp-header-height").each(function () {
      $(this).css({
        height: setHeaderHeight + "px",
      });
    });
  }

  ////////////////////////////////////////////////////
  // 04. Header Class Add Js
  $(".tp-main-menu ul li a").each(function () {
    $(this).wrapInner("<span></span>");
  });

  ////////////////////////////////////////////////////
  // 05. One Page Scroll Js
  function scrollNav() {
    $(".tp-onepage-menu li a").click(function () {
      $(".tp-onepage-menu li a.active").removeClass("active");
      $(this).addClass("active");

      $("html, body")
        .stop()
        .animate(
          {
            scrollTop: $($(this).attr("href")).offset().top - 96,
          },
          300
        );
      return false;
    });
  }
  scrollNav();

  ////////////////////////////////////////////////////
  // 06. Common Js
  $("[data-background").each(function () {
    $(this).css(
      "background-image",
      "url( " + $(this).attr("data-background") + "  )"
    );
  });

  $("[data-width]").each(function () {
    $(this).css("width", $(this).attr("data-width"));
  });

  $("[data-bg-color]").each(function () {
    $(this).css("background-color", $(this).attr("data-bg-color"));
  });

  $("[data-text-color]").each(function () {
    $(this).css("color", $(this).attr("data-text-color"));
  });

  $(".has-img").each(function () {
    var imgSrc = $(this).attr("data-menu-img");
    var img = `<img class="mega-menu-img" src="${imgSrc}" alt="img">`;
    $(this).append(img);
  });

  ////////////////////////////////////////////////////
  // 07. Humburger Js
  $(".tp-hamburger-toggle").on("click", function () {
    $(".tp-header-side-menu").slideToggle("tp-header-side-menu");
  });

  ////////////////////////////////////////////////////
  // 08. Menu Style Js
  if ($(".tp-main-menu-content").length && $(".tp-main-menu-mobile").length) {
    let navContent = document.querySelector(".tp-main-menu-content").outerHTML;
    let mobileNavContainer = document.querySelector(".tp-main-menu-mobile");
    mobileNavContainer.innerHTML = navContent;

    let arrow = $(".tp-main-menu-mobile .has-dropdown > a");

    arrow.each(function () {
      let self = $(this);
      let arrowBtn = document.createElement("BUTTON");
      arrowBtn.classList.add("dropdown-toggle-btn");
      arrowBtn.innerHTML = "<i class='fa-regular fa-angle-right'></i>";

      self.append(function () {
        return arrowBtn;
      });

      self.find("button").on("click", function (e) {
        e.preventDefault();
        let self = $(this);
        self.toggleClass("dropdown-opened");
        self.parent().toggleClass("expanded");
        self
          .parent()
          .parent()
          .addClass("dropdown-opened")
          .siblings()
          .removeClass("dropdown-opened");
        self.parent().parent().children(".submenu").slideToggle();
      });
    });
  }

  ////////////////////////////////////////////////////
  // 09. Search Js
  $(".search-open-btn").on("click", function () {
    $(".search-area").addClass("search-opened");
    $(".search-overlay").addClass("opened");
  });
  $(".search-close-btn").on("click", function () {
    $(".search-area").removeClass("search-opened");
    $(".search-overlay").removeClass("opened");
  });

  ////////////////////////////////////////////////////
  // 10. Offcanvas Js
  $(".offcanvas-open-btn").on("click", function () {
    $(".offcanvas__area").addClass("offcanvas-opened");
    $(".body-overlay").addClass("opened");
  });
  $(
    ".offcanvas-close-btn ,.tp-main-menu-mobile .tp-onepage-menu li a  > *:not(button)"
  ).on("click", function () {
    $(".offcanvas__area").removeClass("offcanvas-opened");
    $(".body-overlay").removeClass("opened");
  });

  ////////////////////////////////////////////////////
  // 11. Body overlay Js
  $(".body-overlay").on("click", function () {
    $(".offcanvas__area").removeClass("offcanvas-opened");
    $(".tp-search-area").removeClass("opened");
    $(".cartmini__area").removeClass("cartmini-opened");
    $(".body-overlay").removeClass("opened");
  });

  ////////////////////////////////////////////////////
  // 12. Nice Select Js
  $("select").not("[required]").niceSelect();
  $(".tp-header-search-category select").niceSelect();

  ////////////////////////////////////////////////////
  // 13. Back To Top Js
  function back_to_top() {
    var btn = $("#back_to_top");
    var btn_wrapper = $(".back-to-top-wrapper");

    windowOn.scroll(function () {
      if (windowOn.scrollTop() > 300) {
        btn_wrapper.addClass("back-to-top-btn-show");
      } else {
        btn_wrapper.removeClass("back-to-top-btn-show");
      }
    });

    btn.on("click", function (e) {
      e.preventDefault();
      $("html, body").animate({ scrollTop: 0 }, "300");
    });
  }
  back_to_top();

  ////////////////////////////////////////////////////
  // Jquery Appear raidal
  if (typeof $.fn.knob != "undefined") {
    $(".knob").each(function () {
      var $this = $(this),
        knobVal = $this.attr("data-rel");

      $this.knob({
        draw: function () {
          $(this.i).val(this.cv + "%");
        },
      });

      $this.appear(
        function () {
          $({
            value: 0,
          }).animate(
            {
              value: knobVal,
            },
            {
              duration: 2000,
              easing: "swing",
              step: function () {
                $this.val(Math.ceil(this.value)).trigger("change");
              },
            }
          );
        },
        {
          accX: 0,
          accY: -150,
        }
      );
    });
  }

  ////////////////////////////////////////////////////
  // Hero Active
  if ($(".tp-hero-active").length > 0) {
    var slider = new Swiper(".tp-hero-active", {
      slidesPerView: 1,
      spaceBetween: 0,
      loop: true,
      effect: "fade",
      autoplay: {
        delay: 5000,
      },
      // Navigation arrows
      navigation: {
        nextEl: ".hero-button-next-1",
        prevEl: ".hero-button-prev-1",
      },
      pagination: {
        el: ".tp-hero-pagination",
        clickable: true,
      },
    });
  }

  ////////////////////////////////////////////////////
  // Project Active
  var slider = new Swiper(".tp-project-active", {
    slidesPerView: 4,
    spaceBetween: 25,
    loop: true,
    breakpoints: {
      1400: {
        slidesPerView: 4,
      },
      1200: {
        slidesPerView: 3,
      },
      992: {
        slidesPerView: 2,
      },
      768: {
        slidesPerView: 2,
      },
      576: {
        slidesPerView: 1,
      },
      0: {
        slidesPerView: 1,
      },
    },
  });

  ////////////////////////////////////////////////////
  // Service Active
  if ($(".tp-service-active").length > 0) {
    var slider = new Swiper(".tp-service-active", {
      slidesPerView: 3,
      spaceBetween: 30,
      loop: true,
      breakpoints: {
        1700: {
          slidesPerView: 3,
        },
        1400: {
          slidesPerView: 3,
        },
        1200: {
          slidesPerView: 3,
        },
        767: {
          slidesPerView: 2,
        },
        576: {
          slidesPerView: 1,
        },
        0: {
          slidesPerView: 1,
        },
      },
      // Navigation arrows
      navigation: {
        nextEl: ".service-button-next-1",
        prevEl: ".service-button-prev-1",
      },
    });
  }

  ////////////////////////////////////////////////////
  // Testimonial Active
  if ($(".tp-testimonial-active").length > 0) {
    var slider = new Swiper(".tp-testimonial-active", {
      slidesPerView: 1,
      spaceBetween: 30,
      loop: true,
      breakpoints: {
        1700: {
          slidesPerView: 2,
        },
        1400: {
          slidesPerView: 2,
        },
        1200: {
          slidesPerView: 2,
        },
        992: {
          slidesPerView: 2,
        },
        767: {
          slidesPerView: 1,
        },
        576: {
          slidesPerView: 1,
        },
        0: {
          slidesPerView: 1,
        },
      },
      // Navigation arrows
      navigation: {
        nextEl: ".testimonial-button-next-1",
        prevEl: ".testimonial-button-prev-1",
      },
    });
  }

  ////////////////////////////////////////////////////
  // Testimonial Active 2
  if ($(".tp-testimonial-2-active").length > 0) {
    var slider = new Swiper(".tp-testimonial-2-active", {
      slidesPerView: 2,
      spaceBetween: 30,
      loop: true,
      breakpoints: {
        1700: {
          slidesPerView: 2,
        },
        1400: {
          slidesPerView: 2,
        },
        1200: {
          slidesPerView: 2,
        },
        992: {
          slidesPerView: 2,
        },
        767: {
          slidesPerView: 1,
        },
        576: {
          slidesPerView: 1,
        },
        0: {
          slidesPerView: 1,
        },
      },
      // Navigation arrows
      navigation: {
        nextEl: ".testimonial-button-next-1",
        prevEl: ".testimonial-button-prev-1",
      },
    });
  }

  ////////////////////////////////////////////////////
  // Testimonial Active 3
  if ($(".tp-testimonial-3-active").length > 0) {
    var slider = new Swiper(".tp-testimonial-3-active", {
      slidesPerView: 2,
      spaceBetween: 30,
      loop: true,
      breakpoints: {
        1700: {
          slidesPerView: 2,
        },
        1400: {
          slidesPerView: 2,
        },
        1200: {
          slidesPerView: 2,
        },
        767: {
          slidesPerView: 2,
        },
        576: {
          slidesPerView: 1,
        },
        0: {
          slidesPerView: 1,
        },
      },
    });
  }

  ////////////////////////////////////////////////////
  // Team Active
  if ($(".tp-team-3-active").length > 0) {
    var slider = new Swiper(".tp-team-3-active", {
      slidesPerView: 3,
      spaceBetween: 30,
      centeredSlides: true,
      loop: true,
      pagination: {
        el: ".slider_pagination",
        clickable: true,
      },
      breakpoints: {
        1700: {
          slidesPerView: 3,
        },
        1400: {
          slidesPerView: 3,
        },
        1200: {
          slidesPerView: 3,
        },
        767: {
          slidesPerView: 3,
        },
        576: {
          slidesPerView: 1,
        },
        0: {
          slidesPerView: 1,
        },
      },
    });
  }

  ////////////////////////////////////////////////////
  // Blog Active
  if ($(".tp-blog-post-active").length > 0) {
    var slider = new Swiper(".tp-blog-post-active", {
      slidesPerView: 1,
      spaceBetween: 30,
      loop: true,
      breakpoints: {
        1700: {
          slidesPerView: 1,
        },
        1400: {
          slidesPerView: 1,
        },
        1200: {
          slidesPerView: 1,
        },
        767: {
          slidesPerView: 1,
        },
        576: {
          slidesPerView: 1,
        },
        0: {
          slidesPerView: 1,
        },
      },
      // Navigation arrows
      navigation: {
        nextEl: ".tp-blog-next-1",
        prevEl: ".tp-blog-prev-1",
      },
    });
  }

  ////////////////////////////////////////////////////
  // 15. Masonary Js
  $(".grid").imagesLoaded(function () {
    // init Isotope
    var $grid = $(".grid").isotope({
      itemSelector: ".grid-item",
      percentPosition: true,
      masonry: {
        // use outer width of grid-sizer for columnWidth
        columnWidth: ".grid-item",
      },
    });

    // filter items on button click
    $(".masonary-menu").on("click", "button", function () {
      var filterValue = $(this).attr("data-filter");
      $grid.isotope({ filter: filterValue });
    });

    //for menu active class
    $(".masonary-menu button").on("click", function (event) {
      $(this).siblings(".active").removeClass("active");
      $(this).addClass("active");
      event.preventDefault();
    });
  });

  /* magnificPopup img view */
  $(".popup-image").magnificPopup({
    type: "image",
    gallery: {
      enabled: true,
    },
  });

  $(".popup-image-footer").magnificPopup({
    type: "image",
    gallery: {
      enabled: true,
    },
  });

  /* magnificPopup video view */
  $(".popup-video").magnificPopup({
    type: "iframe",
  });

  if ($(".scene").length > 0) {
    $(".scene").parallax({
      scalarX: 5.0,
      scalarY: 5.0,
    });
  }

  ////////////////////////////////////////////////////
  // 16. Wow Js
  new WOW().init();

  ////////////////////////////////////////////////////
  // 17. Counter Js
  new PureCounter();
})(jQuery);
