import { Injectable } from '@angular/core';
import { Tweet } from './tweet';
import { Topic } from './topic'
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class TweetsService {
  private tweetApiUrl = '/apis/tweettopic';  // URL to web api
  constructor(private http:HttpClient) { }

  getTweets(): Observable<Tweet[]> {
   return this.http.get<Tweet[]>(this.tweetApiUrl)
    .pipe(
      catchError(this.handleError<Tweet[]>('getTweets', []))
    );
  }

  getRecentTweets(id:String, retweetIncluded:Boolean, query:String):Observable<Tweet[]>{
    const url = `${this.tweetApiUrl}/recent/${id}/`;
    return this.http.get<Tweet[]>(url, {
      params:{
        "retweetIncluded":String(retweetIncluded),
        "query":String(query),
      }})
    .pipe(
      catchError(this.handleError<Tweet[]>('getRecentTweets', []))
    );
  }
  getTopics(){
    const url = `${this.tweetApiUrl}/topics/`;
    return this.http.get<Topic[]>(url)
    .pipe(
      catchError(this.handleError<Topic[]>('getTopics', []))
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
