$(document).ready(function(){

	// Preload images
    // jQuery.preloadCssImages();


	// CSS tweaks
	jQuery('#header #nav li:last').addClass('nobg');
	jQuery('.block_head ul').each(function() { jQuery('li:first', this).addClass('nobg'); });
	jQuery('.block table tr:odd').css('background-color', '#fbfbfb');
	jQuery('.block form input[type=file]').addClass('file');


	// Web stats
	jQuery('table.stats').each(function() {
		var statsType;

		if(jQuery(this).attr('rel')) { statsType = jQuery(this).attr('rel'); }
		else { statsType = 'area'; }

        // console.log(jQuery(this).css('width'));
		if (jQuery(this).css('width') && parseInt(jQuery(this).css('width')) < 880) {
		    width = (parseFloat(jQuery(this).css('width')) / 100) * 880 + 'px';
		} else {
		    width = '880px';
		}

        // console.log(width);

        // jQuery(this).hide().visualize({
        //  type: statsType,    // 'bar', 'area', 'pie', 'line'
        //  width: width,
        //  height: '240px',
        //  colors: ['#6fb9e8', '#ec8526', '#9dc453', '#ddd74c']
        // });
	});


	// Check / uncheck all checkboxes
	jQuery('.check_all').click(function() {
		jQuery(this).parents('form').find('input:checkbox').attr('checked', jQuery(this).is(':checked'));
	});


	// Set WYSIWYG editor
	jQuery('.wysiwyg').wysiwyg({css: "css/wysiwyg.css"});


	// Modal boxes - to all links with rel="facebox"
	jQuery('a[rel*=facebox]').facebox()


	// Messages
	jQuery('.message').hide().append('<span class="close" title="Dismiss"></span>').fadeIn('slow');
	jQuery('.message .close').hover(
		function() { jQuery(this).addClass('hover'); },
		function() { jQuery(this).removeClass('hover'); }
	);

	jQuery('.message .close').click(function() {
		jQuery(this).parent().fadeOut('slow', function() { jQuery(this).remove(); });
	});


	// Form select styling
	jQuery("form select.styled").select_skin();


	// Tabs
	jQuery(".tab_content").hide();
	jQuery("ul.tabs li:first-child").addClass("active").show();
	jQuery(".tab_content:first").show();

	jQuery("ul.tabs li").click(function() {
		jQuery(this).parent().find('li').removeClass("active");
		jQuery(this).addClass("active");
		jQuery(this).parents('.block').find(".tab_content").hide();

		var activeTab = jQuery(this).find("a").attr("href");
		jQuery(activeTab).show();
		return false;
	});


	// Sidebar Tabs
	jQuery(".sidebar_content").hide();
	jQuery("ul.sidemenu li:first-child").addClass("active").show();
	jQuery(".block").find(".sidebar_content:first").show();

	jQuery("ul.sidemenu li").click(function() {
		jQuery(this).parent().find('li').removeClass("active");
		jQuery(this).addClass("active");
		jQuery(this).parents('.block').find(".sidebar_content").hide();

		var activeTab = jQuery(this).find("a").attr("href");
		jQuery(activeTab).show();
		return false;
	});


	// Block search
	jQuery('.block .block_head form .text').bind('click', function() { jQuery(this).attr('value', ''); });


	// Image actions menu
	jQuery('ul.imglist li').hover(
		function() { jQuery(this).find('ul').css('display', 'none').fadeIn('fast').css('display', 'block'); },
		function() { jQuery(this).find('ul').fadeOut(100); }
	);


	// Image delete confirmation
	jQuery('ul.imglist .delete a').click(function() {
		if (confirm("Are you sure you want to delete this image?")) {
			return true;
		} else {
			return false;
		}
	});

	// Navigation dropdown fix for IE6
	if(jQuery.browser.version.substr(0,1) < 7) {
		jQuery('#header #nav li').hover(
			function() { jQuery(this).addClass('iehover'); },
			function() { jQuery(this).removeClass('iehover'); }
		);
	}

	// IE6 PNG fix
	jQuery(document).pngFix();

	$('input:checkbox:not(#schedule input:checkbox):not(#fileset input:checkbox):not(.tree input:checkbox)').not('').iphoneStyle({ checkedLabel: 'Sim', uncheckedLabel: 'Não' });
	$('.filetree').each(function(){
		var script = $(this).attr("ref");
		$(this).fileTree({ root: '/media/lib/demo/', script: script }, function(file) {
			alert(file);
		});
	})
	$(".iPhoneCheckContainer").css("width", "85px");
	// $(".sparklines").sparkline('html', {width: "300", height: "150px" });

});
