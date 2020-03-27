import { Component, OnInit } from '@angular/core';
import { Tweet } from './tweet';
import { Topic } from './topic';
import { TweetsService } from './tweets.service';
import {
  trigger,
  state,
  style,
  animate,
  transition,
} from '@angular/animations';
declare var require: any

@Component({
  selector: 'app-tweets',
  templateUrl: './tweets.component.html',
  styleUrls: ['./tweets.component.css'],
  animations: [
    trigger('items', [
      transition(':enter', [   // :enter is alias to 'void => *'
        style({ height: '0', position: '*' }),
        animate(500, style({ height: '*', position: '*' }))
      ])
    ])
  ]
})
export class TweetsComponent implements OnInit {
  private lastTweetId = '0';
  private tweets: Tweet[] = [];
  private query: String = '';
  private updatedQuery: String = '';
  private retweetIncluded: Boolean = true;
  private topics: Topic[] = [];
  private tweetsByTopic: Tweet[] = [];
  private selectedTopics: Set<number> = new Set<number>();
  constructor(private tweetsService: TweetsService) { }

  ngOnInit() {
    this.updateRecentTweets();
    this.updateTopics();
  }

  updateRecentTweets() {
    this.tweetsService.getRecentTweets(this.lastTweetId,
      this.retweetIncluded, this.updatedQuery).subscribe(tweets => {
        {
          if (tweets.length > 0) {
            tweets = tweets.sort((a, b) => b.id - a.id)
            this.lastTweetId = tweets[0].id.toString();
          }
          this.tweets.unshift(...tweets)
          if (this.tweets.length > 100) {
            this.tweets = this.tweets.slice(0, 100);
          }
          this.tweetsByTopic.unshift(...tweets.filter(
            tw => tw.topic && tw.topic.length &&
              tw.topic.map(t=>this.selectedTopics.has(t)).reduce((x,y)=>x || y))
          );
          if(this.tweetsByTopic.length > 100) {
            this.tweetsByTopic  = this.tweetsByTopic.slice(0,100);
          }
 
          setTimeout(() => this.updateRecentTweets(), 1000);
        }
      });

  }

  updateTopics() {
    this.tweetsService.getTopics().subscribe(
      topics => {
        this.topics = topics;
        var distinctColors = require('distinct-colors').default;
        var palette = distinctColors({count:topics.length});
        topics.forEach(t=>this.topics[t.id].color = palette[t.id].alpha(0.6));
        setTimeout(() => this.updateTopics(), 5000);

      }
    )
  }

  updateQuery(): void {
    let recordedQuery = this.query;
    setTimeout(() => {
      if (recordedQuery == this.query) {
        if (this.query) {
          this.updatedQuery = this.query;
          this.tweets = [];
        } else {
          //code here
        }
      }
    }, 2000);

  }
  onSelectTopic(topic:Topic){
    if (this.selectedTopics.has(topic.id)) {
      this.selectedTopics.delete(topic.id);
    }else{
      this.selectedTopics.add(topic.id);
    }
    this.tweetsByTopic  = [];
  }
}
