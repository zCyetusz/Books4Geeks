console.log("barcode_scanner.js loaded!");

$(function () {
  // Store scanned books
  var scannedBooks = [];
  var isCameraRunning = false;
  
  // Initialize Select2
  $('.select2').select2({
    theme: 'bootstrap4'
  });
  
  // Start scanner button
  $('#start-button').on('click', function() {
    $('#video-feed').attr('src', '/bills/video-feed/');
    $('#start-button').prop('disabled', true);
    $('#stop-button').prop('disabled', false);
  });
  
  // Stop scanner button
  $('#stop-button').on('click', function() {
    $('#video-feed').attr('src', '');
    $('#start-button').prop('disabled', false);
    $('#stop-button').prop('disabled', true);
  });
  
  // Clear button
  $('#clear-button').on('click', function() {
    clearScannedBooks();
  });
  
  // Manual lookup button
  $('#lookup-barcode').on('click', function() {
    var barcode = $('#barcode-manual').val().trim();
    if (barcode) {
      lookupBarcode(barcode);
      $('#barcode-manual').val('');
    }
  });
  
  // Enter key on the manual input
  $('#barcode-manual').on('keypress', function(e) {
    if (e.which === 13) { // Enter key
      $('#lookup-barcode').click();
      e.preventDefault();
    }
  });
  
  // Create bill button
  $('#create-bill-button').on('click', function() {
    createBillFromScannedBooks();
  });
  
  // Lookup a barcode via API
  function lookupBarcode(barcode) {
    $('#loading-spinner').show();
    
    $.ajax({
      url: '/api/get_book_by_barcode/' + barcode + '/',
      type: 'GET',
      success: function(data) {
        if (data.success) {
          // Check if book is already in the list
          var bookExists = false;
          for (var i = 0; i < scannedBooks.length; i++) {
            if (scannedBooks[i].id === data.id) {
              // Increment quantity instead of adding again
              scannedBooks[i].quantity++;
              bookExists = true;
              break;
            }
          }
          
          if (!bookExists) {
            // Add book to the list
            scannedBooks.push({
              id: data.id,
              description: data.description,
              price: data.price,
              quantity: 1,
              publisher: data.publisher,
              authors: data.authors.join(', '),
              categories: data.categories.join(', ')
            });
          }
          
          // Update the display
          updateScannedBooksList();
          
          // Play success sound
          playSound('success');
        } else {
          console.error("Invalid barcode response:", data);
          alert("Could not find book with barcode: " + barcode);
          playSound('error');
        }
      },
      error: function(xhr) {
        console.error("Error looking up barcode:", xhr);
        alert("Error looking up barcode: " + barcode);
        playSound('error');
      },
      complete: function() {
        $('#loading-spinner').hide();
      }
    });
  }
  
  // Update the scanned books list
  function updateScannedBooksList() {
    var container = $('#scanned-books');
    container.empty();
    
    if (scannedBooks.length === 0) {
      container.html('<div class="text-muted text-center"><i class="fas fa-barcode fa-3x mb-3"></i><p>Scan a barcode to add books to the list.</p></div>');
      $('#create-bill-button').prop('disabled', true);
      $('#clear-button').prop('disabled', true);
      return;
    }
    
    var total = 0;
    
    scannedBooks.forEach(function(book, index) {
      var bookTotal = parseFloat(book.price) * book.quantity;
      total += bookTotal;
      
      var itemHtml = '<div class="scan-result">' +
        '<div class="d-flex justify-content-between">' +
        '<h5>' + book.description + '</h5>' +
        '<button class="btn btn-sm btn-danger remove-book" data-index="' + index + '"><i class="fas fa-times"></i></button>' +
        '</div>' +
        '<div class="row">' +
        '<div class="col-md-4"><small class="text-muted">Price: $' + book.price + '</small></div>' +
        '<div class="col-md-4">' +
        '<div class="input-group input-group-sm">' +
        '<div class="input-group-prepend">' +
        '<button class="btn btn-outline-secondary decrease-qty" data-index="' + index + '">-</button>' +
        '</div>' +
        '<input type="number" class="form-control text-center book-quantity" value="' + book.quantity + '" min="1" data-index="' + index + '">' +
        '<div class="input-group-append">' +
        '<button class="btn btn-outline-secondary increase-qty" data-index="' + index + '">+</button>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-4 text-right"><strong>Total: $' + bookTotal.toFixed(2) + '</strong></div>' +
        '</div>' +
        '<div><small class="text-muted">' + (book.authors ? 'By: ' + book.authors : '') + '</small></div>' +
        '<div><small class="text-muted">' + (book.categories ? 'Categories: ' + book.categories : '') + '</small></div>' +
        '</div>';
      
      container.append(itemHtml);
    });
    
    // Add total at the bottom
    container.append('<div class="card-footer text-right"><h4>Grand Total: $' + total.toFixed(2) + '</h4></div>');
    
    // Enable buttons
    $('#create-bill-button').prop('disabled', false);
    $('#clear-button').prop('disabled', false);
    
    // Bind events for quantity changes
    $('.increase-qty').on('click', function() {
      var index = $(this).data('index');
      scannedBooks[index].quantity++;
      updateScannedBooksList();
    });
    
    $('.decrease-qty').on('click', function() {
      var index = $(this).data('index');
      if (scannedBooks[index].quantity > 1) {
        scannedBooks[index].quantity--;
        updateScannedBooksList();
      }
    });
    
    $('.book-quantity').on('change', function() {
      var index = $(this).data('index');
      var qty = parseInt($(this).val());
      if (qty >= 1) {
        scannedBooks[index].quantity = qty;
        updateScannedBooksList();
      } else {
        $(this).val(1);
      }
    });
    
    $('.remove-book').on('click', function() {
      var index = $(this).data('index');
      scannedBooks.splice(index, 1);
      updateScannedBooksList();
    });
  }
  
  // Clear scanned books
  function clearScannedBooks() {
    scannedBooks = [];
    updateScannedBooksList();
  }
  
  // Create a bill from scanned books
  function createBillFromScannedBooks() {
    if (scannedBooks.length === 0) {
      alert('Please scan at least one book before creating a bill.');
      return;
    }
    
    var customerId = $('#customer-select').val();
    if (!customerId) {
      alert('Please select a customer before creating a bill.');
      return;
    }
    
    // Show loading indicator
    $('#loading-spinner').show();
    
    // Use the create_bill_from_scanned API endpoint
    $.ajax({
      url: '/api/create_bill_from_scanned/',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        customer_id: customerId,
        books: scannedBooks
      }),
      success: function(response) {
        if (response.success) {
          alert('Bill created successfully!');
          clearScannedBooks();
          
          // If this is an AJAX page, load the bill list
          if (typeof loadContent === 'function') {
            loadContent("{% url 'bill_list' %}");
          } else {
            // Otherwise redirect to the bill list
            window.location.href = "{% url 'bill_list' %}";
          }
        } else {
          alert('Error creating bill: ' + response.error);
        }
      },
      error: function(xhr) {
        console.error("Error creating bill:", xhr);
        alert('Error creating bill. Please try again.');
      },
      complete: function() {
        $('#loading-spinner').hide();
      }
    });
  }
  
  // Play sound for feedback
  function playSound(type) {
    // Use browser's built-in beep instead of audio files
    if (type === 'success') {
      // High-pitched beep for success
      try {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = context.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.value = 1500;
        oscillator.connect(context.destination);
        oscillator.start();
        setTimeout(function() { oscillator.stop(); }, 200);
      } catch (e) {
        console.log("Audio not supported:", e);
      }
    } else {
      // Low-pitched beep for error
      try {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = context.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.value = 300;
        oscillator.connect(context.destination);
        oscillator.start();
        setTimeout(function() { oscillator.stop(); }, 400);
      } catch (e) {
        console.log("Audio not supported:", e);
      }
    }
  }
  
  // Clean up when leaving the page
  $(window).on('beforeunload', function() {
    if (isCameraRunning) {
      $.ajax({
        url: "{% url 'stop_camera' %}",
        type: 'POST',
        headers: {
          'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        async: false
      });
    }
  });
});