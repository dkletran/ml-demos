import { NgModule } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { AvatarStylingComponent } from './avatarstyling.component';
import { HttpClientModule }    from '@angular/common/http';
import { DeviceDetectorModule } from 'ngx-device-detector';
import { CommonModule } from '@angular/common';  
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    AvatarStylingComponent
  ],
  imports: [
    CommonModule,
    MatCardModule,
    HttpClientModule,
    FormsModule,
    DeviceDetectorModule
  ],
  providers: []
})
export class AvatarStylingModule { }
