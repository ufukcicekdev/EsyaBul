


    $(document).ready(function () {


        $(".edit-address").click(function () {
            var addressId = $(this).data("address-id");
            $.ajax({
                url: `/dashboard/edit_address/${addressId}/`,
                type: "GET",
                success: function (response) {
                    console.log(response.data[0]);
                    var data = response.data[0];
                    $("#addressEditModal input[name='firstName']").val(data.username);
                    $("#addressEditModal input[name='lastName']").val(data.usersurname);
                    $("#addressEditModal input[name='phone']").val(data.phone);
                    $("#addressEditModal input[name='streetAddress']").val(data.address_line1);
                    $("#addressEditModal input[name='title']").val(data.address_name);
                    $("#addressEditModal input[name='corporateName']").val(data.firm_name);
                    $("#addressEditModal input[name='taxNumber']").val(data.firm_taxcode);
                    $("#addressEditModal input[name='taxOffice']").val(data.firm_tax_home);
                    if (data.address_type_id == 2) {
                        $("#addressEditModal input[name='type'][value='2']").prop("checked", true);
                        
                        $(".firm-container, .d-none").removeClass("d-none");
                    } else {
                        $(".firm-container").addClass("d-none");
                        $(".firmName").addClass("d-none");

                    }
                    $("#addressEditModal").css("display", "flex");
                        
                },
                error: function (error) {
                    console.log("Error:", error);
                }
            });
        });

        

        $(".delete-address").click(function () {
            var addressId = document.querySelector('a[data-address-id]').dataset.addressId;
        
            // Django'dan alınan CSRF token'ını çek
            var csrftoken = getCookie('csrftoken');
        
            $.ajax({
                url: `/dashboard/delete_address/${addressId}/`,
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                success: function (response) {
                    if (response.status === "success") {
                        location.reload();
                    } else {
                        alert("Adres silinirken bir hata oluştu.");
                    }
                },
                error: function (error) {
                    console.log("Error:", error);
                }
            });
        });

        $(".update-address").click(function () {
            var addressId = document.querySelector('a[data-address-id]').dataset.addressId;    
            var jsonData = {
                username: $("input[name='firstName']").val(),
                usersurname: $("input[name='lastName']").val(),
                phone: $("input[name='phone']").val(),
                // Diğer alanları ekleyin
    
                cityId: $("input[name='cityId']").val(),
                countyId: $("input[name='countyId']").val(),
                address_line1: $("input[name='streetAddress']").val(),
                title: $("input[name='title']").val(),
                type: $("input[name='type']:checked").val(),
                corporateName: $("input[name='corporateName']").val(),
                taxNumber: $("input[name='taxNumber']").val(),
                taxOffice: $("input[name='taxOffice']").val(),
            };

            var csrftoken = $("[name=csrfmiddlewaretoken]").val();
            $.ajax({
                url: `/dashboard/edit_address/${addressId}/`,
                type: "POST",
                data: JSON.stringify(jsonData),
                dataType: "json", 
                headers: { "X-CSRFToken": csrftoken },
                success: function (response) {
                    location.reload();
                },
                error: function (error) {
                    console.log("Error:", error);
                }
            });
        });

        $("#createAddressBtn").click(function () {
            // Form verilerini al
            var jsonData = {
                username: $("input[name='firstName']").val(),
                usersurname: $("input[name='lastName']").val(),
                phone: $("input[name='phone']").val(),
                // Diğer alanları ekleyin
    
                cityId: $("input[name='cityId']").val(),
                countyId: $("input[name='countyId']").val(),
                address_line1: $("input[name='streetAddress']").val(),
                title: $("input[name='title']").val(),
                type: $("input[name='type']:checked").val(),
                corporateName: $("input[name='corporateName']").val(),
                taxNumber: $("input[name='taxNumber']").val(),
                taxOffice: $("input[name='taxOffice']").val(),
            };
            
            // CSRF token'ı al
            var csrftoken = $("[name=csrfmiddlewaretoken]").val();

            // AJAX ile POST isteği gönder
            $.ajax({
                url:  `/dashboard/create_address/`,
                type: "POST",
                data: JSON.stringify(jsonData),
                dataType: "json", 
                headers: { "X-CSRFToken": csrftoken },
                success: function (response) {
                    console.log("Address created successfully:", response);
                    // Başarılı olduğunda yapılacak işlemler
                },
                error: function (error) {
                    console.log("Error:", error);
                    // Hata durumunda yapılacak işlemler
                }
            });
        });
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // 'csrftoken' adında bir cookie bulunduysa değerini çek
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $(document).ready(function () {
        $("input[name='type']").change(function () {
            var selectedType = $(this).val();
            $(".firm-container").addClass("d-none");
            $(".firmName").addClass("d-none");
            if (selectedType === '2') {
                $(".firm-container").removeClass("d-none");
                $(".firmName").removeClass("d-none");

            }
        });
    });



    function toggleAddressForm() {
        var addressModal = document.getElementById("addressModal");
        if (addressModal.style.display === "none" || addressModal.style.display === "") {
            addressModal.style.display = "flex";
        } else {
            addressModal.style.display = "none";
        }
    }

 

    function editAddress(event) {
        event.preventDefault();
        var addressModal = document.getElementById("addressEditModal");
        if (addressModal.style.display === "none" || addressModal.style.display === "") {
            addressModal.style.display = "flex";
        } else {
            addressModal.style.display = "none";
        }
    }

  
    
    function closeAddressForm1() {
        var addressModal = document.getElementById("addressModal");
        addressModal.style.display = "none";
    }
    function closeAddressForm() {
        var addressModal = document.getElementById("addressEditModal");
        addressModal.style.display = "none";
    }

    