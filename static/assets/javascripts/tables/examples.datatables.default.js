(function( $ ) {

	'use strict';


	var datatableInit = function() {
		var $table 			= $('#datatable-default');
		// var dialog 			= {};
		var $wrapper	= $('#dialog');
		var $cancel 	= $('#dialogCancel');
		var $confirm	= $('#dialogConfirm');

		$table.dataTable();
		
		$table.
			on('click', 'a.remove-row', function(e) {
				e.preventDefault();
				var url = this.href;
				console.log(url);

				$.magnificPopup.open({
						items: {
							src: '#dialog',
							type: 'inline'
						},
						preloader: false,
						modal: true,
						callbacks: {
							change: function() {
								$confirm.on( 'click', function( e ) {
									e.preventDefault();
									window.location.href = url;
									$.magnificPopup.close();
								});
							},
							close: function() {
								$confirm.off( 'click' );
							}
						}
					});
			});

		$cancel.on( 'click', function( e ) {
			e.preventDefault();
			$.magnificPopup.close();
		});	

	};

	$(function() {
		datatableInit();
	});

}).apply( this, [ jQuery ]);