$(window).on('load resize', function() {
   
    //Add/remove class based on browser size when load/resize
    var w = $(window).width();

    if(w >= 1200) {
        // if larger 
        $('#docs-sidebar').addClass('sidebar-visible').removeClass('sidebar-hidden');
    } else {
        // if smaller
        $('#docs-sidebar').addClass('sidebar-hidden').removeClass('sidebar-visible');
    }
});

jQuery(function($) {
    "use strict"; // Start of use strict 
        /* ====== Toggle Sidebar ======= */
        
    $('#docs-sidebar-toggler').on('click', function(){
    
        if ( $('#docs-sidebar').hasClass('sidebar-visible') ) {

                $("#docs-sidebar").removeClass('sidebar-visible').addClass('sidebar-hidden');
            
            
        } else {

                $("#docs-sidebar").removeClass('sidebar-hidden').addClass('sidebar-visible');
            
        }
            
    });
    

    /* ====== Activate scrollspy menu ===== */
    $('body').scrollspy({target: '#docs-nav', offset: 100});
    
    /* ===== Smooth scrolling ====== */
    $('#docs-sidebar a.scrollto').on('click', function(e){
        //store hash
        var target = this.hash;    
        e.preventDefault();
        $('body').scrollTo(target, 800, {offset: -69, 'axis':'y'});
        
        //Collapse sidebar after clicking
        if ($('#docs-sidebar').hasClass('sidebar-visible') && $(window).width() < 1200){
            $('#docs-sidebar').removeClass('sidebar-visible').addClass('slidebar-hidden');
        }
        
    });
    
    /* wmooth scrolling on page load if URL has a hash */
    if(window.location.hash) {
        var urlhash = window.location.hash;
        $('body').scrollTo(urlhash, 800, {offset: -69, 'axis':'y'});
    }
    
    
    /* Bootstrap lightbox */
    /* Ref: http://ashleydw.github.io/lightbox/ */

    $(document).delegate('*[data-toggle="lightbox"]', 'click', function(e) {
        e.preventDefault();
        $(this).ekkoLightbox();
    }); 
    
}); // End of use strict

jQuery(function($) {
    "use strict"; // Start of use strict     
    var upload = null;
    var uploadIsRunning = false;
    var endpoint = '/upload/tus_upload/';
    var chunkSize = 5242880;
    var seqFileDiv1 = $('#sequenceFileChooser');
    var seqFileDiv2 = $('#sequenceFileChooser2');
    var bedFileDiv = $('#bedFileChooser');
    var progressDiv1 = $('#seqProgress');
    var progressDiv2 = $('#seqProgress2');
    var progressDiv3 = $('#bedProgress');
    var progress1 = $('#progressBar');
    var progress2 = $('#progressBar2');
    var progress3 = $('#progressBarBed');
    var toggleBtn1 = $('#toggle-btn');
    var toggleBtn2 = $('#toggle-btn2');
    var toggleBtn3 = $('#toggle-btnbed');
    var uploadSuccess = $('#upload-success');
    var uploadSuccess2 = $('#upload-success2');
    var uploadSuccess3 = $('#upload-successbed');

    var sequenceFile = $("#id_sequence_file");
    var sequenceFileLocation = $("#id_sequence_file_location");
    var sequenceFilename = $("#id_sequence_file_filename");
    var sequenceFile2 = $("#id_sequence_file2");
    var sequenceFileLocation2 = $("#id_sequence_file2_location");
    var sequenceFilename2 = $("#id_sequence_file2_filename");

    var bedFile = $("#id_bed_file");
    var bedFileLocation = $("#id_bed_file_location");
    var bedFilename = $("#id_bed_file_filename");

    if (!tus.isSupported) {
        alertBox.classList.remove("hidden");
    }

    progressDiv1.hide();
    uploadSuccess.hide();
    toggleBtn1.on('click', function () {
        if (upload) {
            if (uploadIsRunning) {
                upload.abort();
                toggleBtn1.html("Resume upload");
                uploadIsRunning = false;
            } else {
                upload.start();
                toggleBtn1.html( "Pause upload");
                uploadIsRunning = true;
            }
        }
    });
    
    progressDiv2.hide();
    uploadSuccess2.hide();
    toggleBtn2.on('click', function () {
        if (upload) {
            if (uploadIsRunning) {
                upload.abort();
                toggleBtn2.html("Resume upload");
                uploadIsRunning = false;
            } else {
                upload.start();
                toggleBtn2.html( "Pause upload");
                uploadIsRunning = true;
            }
        }
    });

    progressDiv3.hide();
    uploadSuccess3.hide();
    toggleBtn3.on('click', function () {
        if (upload) {
            if (uploadIsRunning) {
                upload.abort();
                toggleBtn3.html("Resume upload");
                uploadIsRunning = false;
            } else {
                upload.start();
                toggleBtn3.html( "Pause upload");
                uploadIsRunning = true;
            }
        }
    });
    
    if (sequenceFilename.val()) {
        var changeFileId = sequenceFile.attr('id') + "_changeBtn";
        var successMsg = $("<p><strong>" + sequenceFilename.val() + " </strong> is uploaded. <br /> <a class='btn btn-secondary' id='" + changeFileId +"'>Change file</a></p>");
        seqFileDiv1.hide();
        uploadSuccess.show();
        uploadSuccess.html(successMsg);
        sequenceFile.removeAttr("required");
        jQuery(function($) {
            $('#' + changeFileId).on('click', function(){ 
                uploadSuccess.hide();
                seqFileDiv1.show();
                sequenceFileLocation.val(null)
                sequenceFilename.val(null)
            })
        });
    }

    if (sequenceFilename2.val()) {
        var changeFileId2 = sequenceFile2.attr('id') + "_changeBtn";
        var successMsg = $("<p><strong>" + sequenceFilename2.val() + " </strong> is uploaded. <br /> <a class='btn btn-secondary' id='" + changeFileId2 +"'>Change file</a></p>");
        seqFileDiv2.hide();
        uploadSuccess2.show();
        uploadSuccess2.html(successMsg);
        jQuery(function($) {
            $('#' + changeFileId2).on('click', function(){ 
                uploadSuccess2.hide();
                seqFileDiv2.show();
                sequenceFileLocation2.val(null)
                sequenceFilename2.val(null)
            })
        });
    }

    if (bedFilename.val()) {
        var changeFileId3 = bedFile.attr('id') + "_changeBtn";
        var successMsg = $("<p><strong>" + bedFilename.val() + " </strong> is uploaded. <br /> <a class='btn btn-secondary' id='" + changeFileId3 +"'>Change file</a></p>");
        bedFileDiv.hide();
        uploadSuccess3.show();
        uploadSuccess3.html(successMsg);
        jQuery(function($) {
            $('#' + changeFileId3).on('click', function(){ 
                uploadSuccess3.hide();
                bedFileDiv.show();
                bedFileLocation.val(null)
                bedFilename.val(null)
            })
        });
    }


    sequenceFile.on("change", function () {
        startUpload(sequenceFile, sequenceFileLocation, sequenceFilename, seqFileDiv1, progressDiv1, progress1, toggleBtn1, uploadSuccess);
    });
    
    sequenceFile2.on("change", function () { 
        startUpload(sequenceFile2, sequenceFileLocation2, sequenceFilename2, seqFileDiv2, progressDiv2, progress2, toggleBtn2, uploadSuccess2);
    });
    
    bedFile.on("change", function () { 
        startUpload(bedFile, bedFileLocation, bedFilename, bedFileDiv, progressDiv3, progress3, toggleBtn3, uploadSuccess3);
    });

    function startUpload(sequenceFile, sequenceFileLocation, sequenceFilename, seqFileDiv, progressDiv, progress, toggleBtn, uploadSuccess) {
        seqFileDiv.hide();
        progressDiv.show();
        var file = sequenceFile[0].files[0];
        // Only continue if a file has actually been selected.
        // IE will trigger a change event even if we reset the input element
        // using reset() and we do not want to blow up later.
        if (!file) {
            return;
        }
    
        toggleBtn.textContent = "Pause upload";
    
        var options = {
            endpoint: endpoint,
            chunkSize: chunkSize,
            retryDelays: [0, 1000, 3000, 5000],
            parallelUploads: 1,
            metadata: {
            filename: file.name,
            filetype: file.type
            },
            onError : function (error) {
                if (error.originalRequest) {
                    if (window.confirm("Failed because: " + error + "\nDo you want to retry?")) {
                    upload.start();
                    uploadIsRunning = true;
                    return;
                    }
                } else {
                    window.alert("Failed because: " + error);
                }
                reset(sequenceFile, toggleBtn);    
            },
            onProgress: function (bytesUploaded, bytesTotal) {
                var percentage = (bytesUploaded / bytesTotal * 100).toFixed(2);
                progress.css("width", percentage + "%")
                    .attr("aria-valuenow", percentage)
                    .html(percentage + "%");
                console.log(bytesUploaded, bytesTotal, percentage + "%");
            },
            onSuccess: function () {
                var changeFileId = sequenceFile.attr('id') + "_changeBtn";
                console.log("hey hey", changeFileId)
                var successMsg = $("<p><strong>" + upload.file.name + " (" + upload.file.size + " bytes) </strong> is uploaded. <br /> <a class='btn btn-secondary' id='" + changeFileId +"'>Change file</a></p>");
                sequenceFileLocation.val(upload.url.split('/').pop()) 
                sequenceFilename.val(upload.file.name)              
                sequenceFile.val(null).removeAttr("required");
                console.log(sequenceFileLocation.val(), sequenceFilename.val())
                setTimeout(function(){
                    progressDiv.hide();
                    uploadSuccess.show();
                    uploadSuccess.html(successMsg);
                    jQuery(function($) {
                        $('#' + changeFileId).on('click', function(){ 
                            uploadSuccess.hide();
                            seqFileDiv.show();
                            sequenceFileLocation.val(null)
                            sequenceFilename.val(null)
                        })
                    });
                }, 1000);    
                reset(sequenceFile, toggleBtn);
            }
        };
    
        upload = new tus.Upload(file, options);
        upload.findPreviousUploads().then((previousUploads) => {
            askToResumeUpload(previousUploads, upload, sequenceFile, progressDiv, uploadSuccess);
        });
    }
    
    function reset(sequenceFile, toggleBtn) {
        sequenceFile.val(null)
        toggleBtn.html( "Pause upload")
        upload = null;
        uploadIsRunning = false;
    }

    function askToResumeUpload(previousUploads, upload, sequenceFile, progressDiv, uploadSuccess) {
        console.log(previousUploads)
        if (previousUploads.length === 0) {
            upload.start()
            uploadIsRunning = true;
        }

        previousUploads.sort(function( a, b ) { 
            return new Date(b.creationTime).getTime() - new Date(a.creationTime).getTime(); 
        });
        var sequenceFileStartNewBtn = sequenceFile.attr('id') + "_startNewBtn";
        var sequenceFileResumeBtn = sequenceFile.attr('id') + "_resumeBtn";
        
        var alreadyExist = $("<p><strong>You already started uploading " + upload.file.name + " file at " + previousUploads[0].creationTime + ". Do you want to resume this upload?. <br />" +
         "<a class='btn btn-primary' id='" + sequenceFileResumeBtn + "'>Yes, Resume</a> <a class='btn btn-secondary ml-2' id='" + sequenceFileStartNewBtn + "'>No, Start over</a></p>");
        uploadSuccess.html(alreadyExist);
        uploadSuccess.show();
        progressDiv.hide();

        jQuery(function($) {
            console.log(sequenceFileStartNewBtn, sequenceFileResumeBtn);
            $('#' + sequenceFileStartNewBtn).on('click', function(){ 
                uploadSuccess.hide();
                progressDiv.show();
                upload.start()
                uploadIsRunning = true;
            });
            $('#' + sequenceFileResumeBtn).on('click', function(){ 
                uploadSuccess.hide();
                progressDiv.show();
                upload.resumeFromPreviousUpload(previousUploads[0]);
                upload.start()
                uploadIsRunning = true;
            });
        });
    }
});

