


    $(document).ready(function () {
        $(".edit-address").click(function () {
            var addressId = $(this).data("address-id");
            $.ajax({
                url: `/dashboard/edit_address/${addressId}/`,
                type: "GET",
                success: function (response) {
                    console.log(response.data[0]);
                    var data = response.data[0];
                    $("input[name='firstName']").val(data.username);
                    $("input[name='lastName']").val(data.usersurname);
                    $("input[name='phone']").val(data.phone);
                    $("input[name='streetAddress']").val(data.address_line1);
                    $("input[name='title']").val(data.address_name);
                    $("input[name='corporateName']").val(data.firm_name);
                    $("input[name='taxNumber']").val(data.firm_taxcode);
                    $("input[name='taxOffice']").val(data.firm_tax_home);
                    if (data.address_type_id == 2) {
                        $("input[name='type'][value='2']").prop("checked", true);
                        
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
            if (confirm("Adresi silmek istediğinize emin misiniz?")) {
                var addressId = $(this).data("address-id");
                $.ajax({
                    url: `dashboard/delete_address/${addressId}/`,
                    type: "POST",
                    success: function (response) {
                        if (response.status === "success") {
                            // Silme başarılı, sayfayı yeniden yükle
                            location.reload();
                        } else {
                            alert("Adres silinirken bir hata oluştu.");
                        }
                    },
                    error: function (error) {
                        console.log("Error:", error);
                    }
                });
            }
        });
    });

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

    $("#EditAddressForm").submit(function (event) {
        // Formun normal submit işlemini engelle
        event.preventDefault();

        // Form verilerini al
        var formData = $("#EditAddressForm").serialize();
        var addressId = $(this).data("address-id");
        // AJAX ile POST isteği gönder
        $.ajax({
            url: `/dashboard/edit_address/${addressId}/`,
            type: "POST",
            data: formData,
            success: function (response) {
                // Başarılı olduğunda yapılacak işlemler
                window.location.href = "{% url 'customerauth:address-list' %}";
                console.log("Address updated successfully:", response);
            },
            error: function (error) {
                // Hata durumunda yapılacak işlemler
                console.log("Error:", error);
            }
        });
    });