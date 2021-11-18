import { Component, Input, OnInit } from '@angular/core';
import { FormControlName, FormGroup } from '@angular/forms';
import * as tus from "tus-js-client";

@Component({
  selector: 'app-file-chooser',
  templateUrl: './file-chooser.component.html'
})
export class FileChooserComponent implements OnInit {
  @Input() patient = null;
  @Input() form: FormGroup;
  @Input() fileControlNames = [];

  endpoint = '/api/tus_upload/';
  chunkSize = 5242880;

  assemblies = {
    GRCh38: 'GRCh38 (hg38)',
    GRCh37: 'GRCh37 (hg19)'
  }
  constructor() { }

  ngOnInit(): void {
  }
  get f() { return this.form.controls }
  
  onFileSelect(event, parentObj, fileControlNames){
    var file = event.target.files[0];
    parentObj[fileControlNames[0]] = { percentage: 0, isComplete: false, isAlreadyExist:false, isPaused:false}
    var that = this;
    var upload = new tus.Upload(file, {
      endpoint: this.endpoint,
      chunkSize: this.chunkSize,
      retryDelays: [0, 3000, 5000, 10000, 20000],
      metadata: {
          filename: file.name,
          filetype: file.type
      },
      // Callback for errors which cannot be fixed using retries
      onError: function(error) {
        if (error['originalRequest']) {
          console.log("error:", error);
          console.log(upload)
          var status = error['originalRequest'] ? error['originalRequest'].getStatus() : 0
          if (status == 403) {
            console.log("Failed because: " + error)
          } else {

          }
        } else {
          window.alert("Failed because: " + error);
          // reset(sequenceFile, toggleBtn, upload);  
        }  
      },
      // Callback for reporting upload progress
      onProgress: function(bytesUploaded, bytesTotal) {
          parentObj[fileControlNames[0]]['percentage'] = (bytesUploaded / bytesTotal * 100).toFixed(2);
          console.log(bytesUploaded, bytesTotal, parentObj[fileControlNames[0]]['percentage'] + "%")
      },
      // Callback for once the upload is completed
      onSuccess: function() {
          console.log("Download %s from %s", file.name, upload.url)
          parentObj[fileControlNames[0]].isComplete = true;
          parentObj[fileControlNames[0]]['fileLocation'] = upload.url.split('/').pop(); 
          parentObj[fileControlNames[0]]['filename'] = file.name;
          console.log(that.form.value, fileControlNames);
          that.f[fileControlNames[1]].setValue(upload.url.split('/').pop());
          that.f[fileControlNames[2]].setValue(file.name);
          console.log("here", that.form.value);
      }
  });

    parentObj[fileControlNames[0]]['upload'] = upload;
    // Check if there are any previous uploads to continue.
    upload.findPreviousUploads().then(previousUploads => {
        this.askToResumeUpload(previousUploads, upload, parentObj[fileControlNames[0]]);
    });
  }

  onChangeFile(obj, fileControlNames){
    this.reset(obj[fileControlNames[0]], fileControlNames);
    obj[fileControlNames[0]] = null;
  }

  onPauseFile(sequenceFileObj){
    sequenceFileObj.upload.abort();
    sequenceFileObj.isPaused = true;
  }


  onResumeFile(sequenceFileObj) {
    sequenceFileObj.upload.start();
    sequenceFileObj.isPaused = false;
    sequenceFileObj.isComplete = false;
  }


  reset(sequenceFileObj, fileControlNames) {
    this.f[fileControlNames[0]].setValue(null);
    this.f[fileControlNames[1]].setValue(null);
    this.f[fileControlNames[2]].setValue(null);
    sequenceFileObj.upload = null;
    sequenceFileObj = null;
  }

  onResumeOldFile(sequenceFileObj){
    sequenceFileObj.upload.resumeFromPreviousUpload(sequenceFileObj.previousUploads[0]);
    this.onResumeFile(sequenceFileObj);
    sequenceFileObj.isAlreadyExist = false;
  }

  onStartFile(sequenceFileObj){
    sequenceFileObj.upload.start();
    sequenceFileObj.isAlreadyExist = false;
    sequenceFileObj.isComplete = false;
  }

  askToResumeUpload(previousUploads, upload, sequenceFileObj) {
    if (previousUploads.length === 0) {
        upload.start()
        return
    }

    previousUploads.sort(function( a, b ) { 
        return new Date(b.creationTime).getTime() - new Date(a.creationTime).getTime(); 
    });
    
    sequenceFileObj.isAlreadyExist = true;
    sequenceFileObj.isComplete = false;
    sequenceFileObj['previousUploads'] = previousUploads; 
    console.log("here", previousUploads, upload, sequenceFileObj)
  }

  keys = Object.keys;
}
