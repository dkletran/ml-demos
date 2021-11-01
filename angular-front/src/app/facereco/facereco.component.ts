import { Component, ElementRef, OnInit, Renderer2, ViewChild } from '@angular/core';
import { DeviceDetectorService } from 'ngx-device-detector';
import { FaceService } from './face.service'
import * as fixRotation from 'src/app/shared/fix-rotation'

@Component({
  selector: 'app-facereco',
  templateUrl: './facereco.component.html',
  styleUrls: [
    './facereco.component.css',
  ]
})
export class FaceRecoComponent implements OnInit {
  @ViewChild('video', { static: true }) videoElement: ElementRef;
  @ViewChild('canvas', { static: true }) canvas: ElementRef;
  videoWidth = 0;
  videoHeight = 0;
  constraints = {
    video: {
      facingMode: "environment",
      width: { ideal: 4096 },
      height: { ideal: 2160 }
    }
  };
  photoCaptured = false;
  faceImages = [];
  identifiedFaces = [];
  newCanvas = document.createElement('canvas');
  loadingLocalImage = false;
  identifying = false;
  cameraOn = false;
  isDesktop: Boolean;
  browseButtonLabel: String;
  constructor(
    private renderer: Renderer2,
    private faceService: FaceService,
    private deviceService: DeviceDetectorService,
  ) {

  }

  ngOnInit() {
    if (this.deviceService.isDesktop()) {
      this.isDesktop = true;
      this.browseButtonLabel = "Select Local Image";
    } else {
      this.isDesktop = false;
      this.browseButtonLabel = "Take a photo";
    }
  }

  startCamera() {
    if (!!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) {
      navigator.mediaDevices.getUserMedia(this.constraints)
        .then(this.attachVideo.bind(this)).catch(this.handleError);
      this.cameraOn = true;
    } else {
      alert('Sorry, camera not available.');
    }
  }

  stopCamera() {
    this.videoElement.nativeElement['srcObject']
      .getTracks().map(x => x.stop());
    this.cameraOn = false;
  }

  attachVideo(stream) {
    this.renderer.setProperty(this.videoElement.nativeElement, 'srcObject', stream);
    this.renderer.listen(this.videoElement.nativeElement, 'play', (event) => {
      this.videoHeight = this.videoElement.nativeElement.videoHeight;
      this.videoWidth = this.videoElement.nativeElement.videoWidth;
    });
  }

  capture() {
    this.renderer.setProperty(this.canvas.nativeElement, 'width', this.videoWidth);
    this.renderer.setProperty(this.canvas.nativeElement, 'height', this.videoHeight);
    this.canvas.nativeElement.getContext('2d').drawImage(this.videoElement.nativeElement, 0, 0);
    this.photoCaptured = true;
    this.stopCamera();
  }

  drawLocalImage(event) {
    this.loadingLocalImage = true;
    var files = event.target.files;
    if (files.length === 0) {
      this.loadingLocalImage = false;
      return;
    }

    // For this example we only want one image. We'll take the first.
    var file = files[0];
    fixRotation.fixRotation([file]).then(
      blobs => {
        var reader = new FileReader();
        // Read in the image file as a data URL.
        reader.readAsDataURL(blobs[0]);
        reader.onload = (evt => {
          if (evt.target.readyState == FileReader.DONE) {
            var img = new Image()
            img.onload = () => {
              this.renderer.setProperty(this.canvas.nativeElement, 'width', img.width);
              this.renderer.setProperty(this.canvas.nativeElement, 'height', img.height);
              this.canvas.nativeElement.getContext('2d').drawImage(img, 0, 0)
              this.loadingLocalImage = false;
            };
            img.src = evt.target.result;
            this.photoCaptured = true;
          }
        }).bind(this);
      }
    );


  }

  putFaceName(inputbox, face, spinner, check) {
    if (inputbox.value) {
      inputbox.disabled = true;
      spinner.hidden = false;
      this.faceService.tagFace(face, inputbox.value).subscribe(
        response => {
          if (response == 'OK') {
            check.hidden = false;
            spinner.hidden = true;
          } else {
            inputbox.disabled = false;
            spinner.hidden = false;
          }
        });
    }

  }

  identifyFaces() {
    this.identifying = true;
    this.identifiedFaces = [];
    setTimeout(
      () => this.faceService.identifyFaces(
        this.canvas.nativeElement.toDataURL()
      )
        .subscribe(
          faceBoxes => {
            this.identifiedFaces = faceBoxes;
            this.identifying = false;
          })
    );
  }
  handleError(error) {
    console.log('Error: ', error);
  }

}