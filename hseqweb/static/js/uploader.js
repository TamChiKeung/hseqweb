jQuery(function($) {
    "use strict"; // Start of use strict 
    var endpoint = '/upload/tus_upload/';
    var chunkSize = 5242880;

    //seq file chooser 1
    var seqFileDiv1 = $('#sequenceFileChooser');
    var progressDiv1 = $('#seqProgress');
    var progress1 = $('#progressBar');
    var toggleBtn1 = $('#toggle-btn');
    var uploadSuccess = $('#upload-success');

    var sequenceFile = $("#id_sequence_file");
    var sequenceFileLocation = $("#id_sequence_file_location");
    var sequenceFilename = $("#id_sequence_file_filename");    
    var uploadSeqFile = {upload: null, isRunning: false}

    //seq file chooser 2
    var seqFileDiv2 = $('#sequenceFileChooser2');
    var progressDiv2 = $('#seqProgress2');
    var progress2 = $('#progressBar2');
    var toggleBtn2 = $('#toggle-btn2');
    var uploadSuccess2 = $('#upload-success2');

    var sequenceFile2 = $("#id_sequence_file2");
    var sequenceFileLocation2 = $("#id_sequence_file2_location");
    var sequenceFilename2 = $("#id_sequence_file2_filename");
    var uploadSeqFile2 = {upload: null, isRunning: false}

    //variant region file chooser
    var bedFileDiv = $('#bedFileChooser');
    var progressDiv3 = $('#bedProgress');
    var progress3 = $('#progressBarBed');
    var toggleBtn3 = $('#toggle-btnbed');
    var uploadSuccess3 = $('#upload-successbed');

    var bedFile = $("#id_bed_file");
    var bedFileLocation = $("#id_bed_file_location");
    var bedFilename = $("#id_bed_file_filename");
    var uploadBedFile = {upload: null, isRunning: false}

    if (!tus.isSupported) {
        alertBox.classList.remove("hidden");
    }

    progressDiv1.hide();
    uploadSuccess.hide();
    toggleBtn1.on('click', function () {
        if (uploadSeqFile.upload) {
            if (uploadSeqFile.isRunning) {
                uploadSeqFile.upload.abort();
                toggleBtn1.html("Resume");
                uploadSeqFile.isRunning = false;
            } else {
                uploadSeqFile.upload.start();
                toggleBtn1.html( "Pause");
                uploadSeqFile.isRunning = true;
            }
        }
    });
    
    progressDiv2.hide();
    uploadSuccess2.hide();
    toggleBtn2.on('click', function () {
        if (uploadSeqFile2.upload) {
            if (uploadSeqFile2.isRunning ) {
                uploadSeqFile2.upload.abort();
                toggleBtn2.html("Resume");
                uploadSeqFile2.isRunning = false;
            } else {
                uploadSeqFile2.upload.start();
                toggleBtn2.html( "Pause");
                uploadSeqFile2.isRunning = true;
            }
        }
    });

    progressDiv3.hide();
    uploadSuccess3.hide();
    toggleBtn3.on('click', function () {
        if (uploadBedFile.upload) {
            if (uploadBedFile.isRunning) {
                uploadBedFile.upload.abort();
                toggleBtn3.html("Resume");
                uploadBedFile.isRunning = false;
            } else {
                uploadBedFile.upload.start();
                toggleBtn3.html( "Pause");
                uploadBedFile.isRunning = true;
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
        startUpload(sequenceFile, sequenceFileLocation, sequenceFilename, seqFileDiv1, progressDiv1, progress1, toggleBtn1, uploadSuccess, uploadSeqFile);
    });
    
    sequenceFile2.on("change", function () { 
        startUpload(sequenceFile2, sequenceFileLocation2, sequenceFilename2, seqFileDiv2, progressDiv2, progress2, toggleBtn2, uploadSuccess2, uploadSeqFile2);
    });
    
    bedFile.on("change", function () { 
        startUpload(bedFile, bedFileLocation, bedFilename, bedFileDiv, progressDiv3, progress3, toggleBtn3, uploadSuccess3, uploadBedFile);
    });

    function startUpload(sequenceFile, sequenceFileLocation, sequenceFilename, seqFileDiv, progressDiv, progress, toggleBtn, uploadSuccess, upload) {
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
                        upload.upload.start();
                        upload.isRunning = true;
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
                console.log("uploaded", changeFileId)
                var successMsg = $("<p><strong>" + upload.upload.file.name + " (" + upload.upload.file.size + " bytes) </strong> is uploaded. <br /> <a class='btn btn-secondary' id='" + changeFileId +"'>Change file</a></p>");
                sequenceFileLocation.val(upload.upload.url.split('/').pop()) 
                sequenceFilename.val(upload.upload.file.name)              
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
                reset(sequenceFile, toggleBtn, upload);
            }
        };
    
        upload.upload = new tus.Upload(file, options);
        console.log("uplaod object:", upload);
        upload.upload.findPreviousUploads().then((previousUploads) => {
            askToResumeUpload(previousUploads, upload, sequenceFile, progressDiv, uploadSuccess);
        });
    }
    
    function reset(sequenceFile, toggleBtn, upload) {
        sequenceFile.val(null)
        toggleBtn.html( "Pause")
        upload.upload = null;
        upload.isRunning = false;
    }

    function askToResumeUpload(previousUploads, upload, sequenceFile, progressDiv, uploadSuccess) {
        console.log(previousUploads)
        if (previousUploads.length === 0) {
            upload.upload.start()
            upload.isRunning = true;
        }

        previousUploads.sort(function( a, b ) { 
            return new Date(b.creationTime).getTime() - new Date(a.creationTime).getTime(); 
        });
        var sequenceFileStartNewBtn = sequenceFile.attr('id') + "_startNewBtn";
        var sequenceFileResumeBtn = sequenceFile.attr('id') + "_resumeBtn";
        
        var alreadyExist = $("<p><strong>You already started uploading " + upload.upload.file.name + " file at " + previousUploads[0].creationTime + ". Do you want to resume this upload?. <br />" +
         "<a class='btn btn-primary' id='" + sequenceFileResumeBtn + "'>Yes, Resume</a> <a class='btn btn-secondary ml-2' id='" + sequenceFileStartNewBtn + "'>No, Start over</a></p>");
        uploadSuccess.html(alreadyExist);
        uploadSuccess.show();
        progressDiv.hide();

        jQuery(function($) {
            $('#' + sequenceFileStartNewBtn).on('click', function(){ 
                uploadSuccess.hide();
                progressDiv.show();
                upload.upload.start()
                upload.isRunning = true;
            });
            $('#' + sequenceFileResumeBtn).on('click', function(){ 
                uploadSuccess.hide();
                progressDiv.show();
                upload.upload.resumeFromPreviousUpload(previousUploads[0]);
                upload.upload.start()
                upload.isRunning = true;
            });
        });
    }
});

