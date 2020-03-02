import { NgModule } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { FaceRecoComponent } from './facereco.component';
import { HttpClientModule }    from '@angular/common/http';
import { DeviceDetectorModule } from 'ngx-device-detector';
import { CommonModule } from '@angular/common';  

@NgModule({
  declarations: [
    FaceRecoComponent
  ],
  imports: [
    CommonModule,
    MatCardModule,
    HttpClientModule,
    DeviceDetectorModule
  ],
  providers: []
})
export class FaceRecoModule { }
