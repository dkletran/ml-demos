import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { FaceBox } from './face-box';
@Injectable({
  providedIn: 'root'
})
export class FaceService {
  private faceApiUrl = '/apis/facereco';  // URL to web api
  constructor(private http:HttpClient) { }

  tagFace(base64Img:String, name:String):Observable<String>{
    const url = `${this.faceApiUrl}/tag_face/`;
    return this.http.post<String>(url, {'face':base64Img, 'name':name})
    .pipe(
      catchError(this.handleError<String>('tagFace', 'ERROR'))
    );
  }

  identifyFaces(base64Img:String):Observable<FaceBox[]>{
    const url = `${this.faceApiUrl}/face_identify/`;
    return this.http.post<FaceBox[]>(url, base64Img)
    .pipe(
      catchError(this.handleError<FaceBox[]>('detectFaces', []))
    );
  }

  private handleError<T> (operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
  
      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead
  
      // TODO: better job of transforming error for user consumption
  
      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }
}
