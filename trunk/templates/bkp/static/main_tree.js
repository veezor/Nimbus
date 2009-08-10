$(document).ready(
    function() {
        // Start tree.
        tree = $('.filetree').treeview(
            {animated: 'fast', collapsed: true, cookie: true, persist: "cookie"}
        );
        
        // Populate tree values.
        tree.find('input').each(
            function() {
                my_obj = $(this);
                my_obj.parent().parents().filter('li').each(
                    function () {
                        folder_name = $(this).children().filter('span').html();
                        my_obj.attr('value', folder_name + my_obj.attr('value'));
                    }
                )
            }
        );
        
        // Update cache values.
        cache_selected = $.cookie('cache_selected');
        if (cache_selected) {
            cache_selected = cache_selected.split(';');
            $(cache_selected).each(
                function() {
                    if (this.substr(0, 4) == 'dir_') {
                        dir = this.split('_', 2);
                        $('*[name=dir][value="' + dir[1] + '"]').attr('checked', true);
                    } else {
                        $('*[name=' + this + ']').attr('checked', true);
                    }
                }
            );
        }
        
        // Binds input click.
        tree.find('input').click(
            function() {
                // Check all childs of this element.
                $(this).parent().find('input').attr(
                    'checked', $(this).attr('checked'));
                
                // Verify if all siblings are checkeds.
                siblings = $(this).parent().siblings().children().filter('input');
                check_siblings(this, siblings);
            }
        );
        
        // Check for siblings checkeds box.
        function check_siblings(_this, siblings) {
            siblings_checked = true;
            siblings.each(
                function() {
                    if (!$(this).attr('checked')) {
                        siblings_checked = false;
                    }
                }
            );
            
            if (!$(_this).attr('checked')) {
                siblings_checked = false;
            }
            
            parent_input = $(_this).parent().parent().parent().children().filter('input');
            if (siblings_checked) {
                parent_input.attr('checked', true);
            } else {
                parent_input.attr('checked', false);
            }
        }
        
        // Bind submit to restore form.
        $('form#form_restore').submit(function() {
            // Cookie all selected files.
            cache_selected = [];
            serialized_inputs = tree.find('input').serializeArray();
            $(serialized_inputs).each(
                function() {
                    name = this.name;
                    if (this.name == 'dir') {
                        name = this.name + '_' + this.value;
                    }
                    cache_selected.push(name);
                }
            );
            if (cache_selected) {
                $.cookie('cache_selected', cache_selected.join(';'),
                         {path: '/', expires: 10});
            }
            
            with_files = false;
            $(this).serializeArray().filter(
                function(obj){
                    if (obj.name.substr(0, 5) == 'file_') {
                        with_files = true;
                    }
                }
            );
            
            // If no one input is selected, form will not be submitted
            if (!with_files || !$(this).serialize()) {
                alert('Selecione pelo menos um arquivo para restauração.');
                return false;
            }
            
            $('*[rel=tree_select_input]').each(function(){
                if ($(this).attr('checked')) {
                    $('*[rel=' + $(this).attr('id') + ']').attr('disabled', true);
                }
            });
        });
    }
);
