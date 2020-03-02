import { NgModule }             from '@angular/core';
import { RouterModule, Routes, NoPreloading } from '@angular/router';
import { FaceRecoComponent } from './facereco/facereco.component'
const appRoutes: Routes = [
  {
    path: 'facereco',
    component: FaceRecoComponent
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(
      appRoutes,
      {
        enableTracing: false, // <-- debugging purposes only
        preloadingStrategy: NoPreloading,
      }
    )
  ],
  exports: [
    RouterModule
  ]
})
export class AppRoutingModule { }
