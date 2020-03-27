import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule }    from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { NgxLinkifyjsModule } from 'ngx-linkifyjs';
import { MatTabsModule } from '@angular/material/tabs';
import { TweetsComponent } from './tweets.component';
import { MatGridListModule } from '@angular/material/grid-list';

@NgModule({
  declarations: [
    TweetsComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MatListModule,
    MatCardModule,
    MatInputModule,
    FormsModule,
    MatCheckboxModule,
    MatTabsModule,
    NgxLinkifyjsModule.forRoot(),
    HttpClientModule,
    MatGridListModule
  ],
  providers: []
})
export class TweetModule { }
