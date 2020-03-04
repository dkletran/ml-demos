import { Component, ElementRef, OnInit, Renderer2, ViewChild } from '@angular/core';
import { DeviceDetectorService } from 'ngx-device-detector';
import { AvatarStylingService } from './avatarstyling.service'
declare var require: any

@Component({
  selector: 'app-avatarstyling',
  templateUrl: './avatarstyling.component.html',
  styleUrls: [
    './avatarstyling.component.css',
  ]
})
export class AvatarStylingComponent implements OnInit {
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
  newCanvas = document.createElement('canvas');
  loadingLocalImage = false;
  cropping = false;
  cameraOn = false;
  isDesktop: Boolean;
  browseButtonLabel: String;
  avatars = [];
  styleFace: Boolean = false;
  styleHair : Boolean = false;
  styleHalf: Boolean = false;
  styleHalfSide: String = "";
  styling = false;
  styledAvatar:String;
  faceHairOnly:false;
  constructor(
    private renderer: Renderer2,
    private deviceService: DeviceDetectorService,
    private avatarStylingService : AvatarStylingService
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
    let fixRotation = require('fix-image-rotation');
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

  cropAvatar() {
    this.cropping = true;
    this.avatars = [];
    setTimeout(
      () => this.avatarStylingService.cropAvatar(
        this.canvas.nativeElement.toDataURL()
      )
        .subscribe(
          avatarBoxes => {
            let orgUrl= this.canvas.nativeElement.toDataURL();
            
            avatarBoxes.map (
              box =>{
                var image = new Image();
                let crop_canvas =  document.createElement('canvas');
                crop_canvas.width = box.width;
                crop_canvas.height = box.height;
                image.onload = ()=>{
                  crop_canvas.getContext('2d').drawImage(image, box.x, box.y, box.width, box.height, 0, 0, box.width, box.height);
                  this.avatars.push(crop_canvas.toDataURL());
                }
                image.src = orgUrl;
              }
            );
            this.cropping = false;
          })
    );
  }
  styleAvatar(){
    this.styling = true;
    if(!this.styleHalf){
      this.styleHalfSide = '';
    }
    this.avatarStylingService.styleAvatar(
      this.avatars[0],
      this.styleFace,
      this.styleHair,
      this.styleHalfSide,
      this.faceHairOnly
    ).subscribe(
      styledAvatar =>{
        this.styling = false;
        this.styledAvatar = styledAvatar;
      }
    )
    
  }
  handleError(error) {
    console.log('Error: ', error);
  }

}