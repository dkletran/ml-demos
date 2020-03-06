import { NgModule }             from '@angular/core';
import { RouterModule, Routes, NoPreloading } from '@angular/router';
import { FaceRecoComponent } from './facereco/facereco.component'
import { AvatarStylingComponent } from './avatarstyling/avatarstyling.component'
const appRoutes: Routes = [
  {
    path: 'facereco',
    component: FaceRecoComponent,
  },
  {
    path: 'avatarstyling',
    component: AvatarStylingComponent
  },
  {
    path: '**', 
     redirectTo: '/404'
  }

];

@NgModule({
  imports: [
    RouterModule.forRoot(
      appRoutes,
      {
        enableTracing: false, // <-- debugging purposes only
        preloadingStrategy: NoPreloading,
        initialNavigation : false,
      }
    )
  ],
  exports: [
    RouterModule
  ]
})
export class AppRoutingModule { }
