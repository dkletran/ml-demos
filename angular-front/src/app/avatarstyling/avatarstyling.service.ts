import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { AvatarBox } from './avatar-box';
@Injectable({
  providedIn: 'root'
})
export class AvatarStylingService {
  private avatarApi = '/avatarstyling/api';  // URL to web api
  constructor(private http: HttpClient) { }


  cropAvatar(base64Img: String): Observable<AvatarBox[]> {
    const url = `${this.avatarApi}/crop_avatar/`;
    return this.http.post<AvatarBox[]>(url, base64Img)
      .pipe(
        catchError(this.handleError<AvatarBox[]>('cropAvatar', []))
      );
  }

  styleAvatar(base64Img: String, styleFace: Boolean,
    styleHair: Boolean, styleSide: String, faceHairOnly: Boolean): Observable<String> {
    const url = `${this.avatarApi}/style_avatar/`;
    return this.http.post<String>(url, {
      'image': base64Img, 'styleFace': styleFace,
      'styleHair': styleHair, 'styleSide': styleSide,
      'faceHairOnly':faceHairOnly
    })
      .pipe(
        catchError(this.handleError<String>('styleAvatar', 'ERROR'))
      );
  }

  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead

      // TODO: better job of transforming error for user consumption

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }
}
