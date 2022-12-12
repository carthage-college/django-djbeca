/* spinner: instantiate */
var opts = {
  lines: 13, // The number of lines to draw
  length: 20, // The length of each line
  width: 10, // The line thickness
  radius: 30, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb or array of colors
  speed: 1, // Rounds per second
  trail: 60, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'search-results', // The CSS class to assign to spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: '50px', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
};
var target = document.getElementById('alert-container');
var spinner = new Spinner(opts).spin(target);
spinner.stop(target);

/**
* simple function to show/hide an element based on the value
* of another dom object
**/
function toggle(dis, val, dom) {
  if (dis == val) {
    $(dom).show();
  } else {
    $(dom).hide();
  }
}

/* jquery onload method */
$(function() {
  /* added 'required' class to form inputs */
  $(".required > input").addClass("required");
  $(".required > select").addClass("required");
  $(".required > textarea").addClass("required");
  $(".warning > input").addClass("error");
  $(".warning > select").addClass("error");
  $(".warning > textarea").addClass("error");
  $(".required > ul").parent().parent().find('h3').addClass("required");

  /* bootstrap tool tip */
  $('[data-toggle="tooltip"]').tooltip();
  /* print page */
  $('#print').click(function() {
    window.print();
    return false;
  });
  /* datepicker */
  $('#id_interaction_date').datepicker({
    firstDay:0,
    maxDate: new Date,
    changeFirstDay:false,
    dateFormat:'yy-mm-dd',
    buttonImage:'//www.carthage.edu/themes/shared/img/ico/calendar.gif',
    showOn:'both',
    buttonImageOnly:true
  });
  /* wysiwyg for textarea fields */
  var $trumBowygDict = {
    btns: [
      ['formatting'], ['strong', 'em', 'del'], ['link'],
      ['unorderedList', 'orderedList'], ['horizontalRule'], ['viewHTML'],
    ],
    tagsToRemove: ['script', 'link'], urlProtocol: true,
    removeformatPasted: true, semantic: true, autogrow: true, resetCss: true
  };
  $('textarea').trumbowyg($trumBowygDict);
  /* clear django cache object by cache key and refresh content */
  $('.clear-cache').on('click', function(e){
    e.preventDefault();
    var $dis = $(this);
    var $cid = $dis.attr('data-cid');
    var $target = '#' + $dis.attr('data-target');
    var $html = $dis.html();
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: 'POST',
      url: $clearCacheUrl,
      data: {'cid':$cid},
      success: function(data) {
        $.growlUI("Cache", "Clear");
        $($target).html(data);
        $dis.html('<i class="fa fa-refresh"></i>');
      },
      error: function(data) {
        $.growlUI("Error", data);
      }
    });
    return false;
  });
  /* datatables initialization */
  $('.data-table').DataTable({
    dom: 'lfrBtip',
    bFilter: false,
    paging: false,
    info: false,
    buttons: [],
    stripeClasses: [],
    order: [[ 1, 'asc' ]]
  });
  $('.history-table').DataTable({
    dom: 'lfrBtip',
    bFilter: false,
    paging: false,
    info: false,
    buttons: [],
    stripeClasses: [],
    order: [[ 2, 'desc' ]]
  });
  $('.sos-matrix').DataTable({
    'lengthMenu': [
      [15], [15]
    ],
    dom: 'lfrBtip',
    buttons: [],
    stripeClasses: [],
    info: false,
    paging: true,
    lengthChange: false,
    searching: true
  });
  $('.faculty-staff').DataTable({
    'lengthMenu': [
      [15], [15]
    ],
    dom: 'lfrBtip',
    buttons: [],
    stripeClasses: [],
    info: false,
    paging: true,
    lengthChange: false,
    searching: true
  });
  var alertTable = $('#data-table').DataTable({
    'lengthMenu': [
      [25, 50, 100, 250, 500, 1000, 2000, -1],
      [25, 50, 100, 250, 500, 1000, 2000, 'All']
    ],
    dom: 'lfrBtip',
    buttons: [
      'csv', 'excel'
    ]
  });
  $('#confirm-delete').on('show.bs.modal', function(e) {
    $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
    $('.object-title').text( $(e.relatedTarget).data('title') );
  });
  /* override the submit event for the alert form to handle some things */
  $('form#alert-form').submit(function(){
    // set the value of the student field to email address selected
    // via autocomplete
    $('#autoComplete').val($('#autoComplete').attr('data-email'));
    /* check textarea for just br tag */
    $('textarea').each(function(){
      if (this.value == '<br>') {
          this.value = '';
      }
    });
    // disable submit button after users clicks it
    $(this).children('input[type=submit]').attr('disabled', 'disabled');
  });
});
