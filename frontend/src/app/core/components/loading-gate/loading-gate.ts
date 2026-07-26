import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, output, signal } from '@angular/core';
import gsap from 'gsap';

@Component({
  selector: 'app-loading-gate',
  imports: [],
  templateUrl: './loading-gate.html',
  styleUrl: './loading-gate.scss',
})
export class LoadingGate implements AfterViewInit, OnDestroy {
  readonly timedOut = signal(false);
  readonly retryRequested = output<void>();

  @ViewChild('nodeClient') private nodeClient!: ElementRef<SVGGElement>;
  @ViewChild('nodeLb') private nodeLb!: ElementRef<SVGGElement>;
  @ViewChild('nodeServer1') private nodeServer1!: ElementRef<SVGGElement>;
  @ViewChild('nodeServer2') private nodeServer2!: ElementRef<SVGGElement>;
  @ViewChild('nodeDb') private nodeDb!: ElementRef<SVGGElement>;
  @ViewChild('lineClientLb') private lineClientLb!: ElementRef<SVGLineElement>;
  @ViewChild('lineLbServer1') private lineLbServer1!: ElementRef<SVGLineElement>;
  @ViewChild('lineLbServer2') private lineLbServer2!: ElementRef<SVGLineElement>;
  @ViewChild('lineServer1Db') private lineServer1Db!: ElementRef<SVGLineElement>;
  @ViewChild('lineServer2Db') private lineServer2Db!: ElementRef<SVGLineElement>;

  private timeline?: gsap.core.Timeline;

  statusText(): string {
    return this.timedOut()
      ? 'Still waking up the backend…'
      : 'Waking up the backend…';
  }

  hintText(): string {
    return this.timedOut()
      ? 'This is taking longer than usual. You can keep waiting or retry.'
      : 'First load can take up to a minute.';
  }

  ngAfterViewInit(): void {
    this.timeline = this.buildTimeline();
  }

  ngOnDestroy(): void {
    this.timeline?.kill();
  }

  markTimedOut(): void {
    this.timedOut.set(true);
  }

  retry(): void {
    this.timedOut.set(false);
    this.retryRequested.emit();
  }

  private buildTimeline(): gsap.core.Timeline {
    const nodes = [
      this.nodeClient.nativeElement,
      this.nodeLb.nativeElement,
      this.nodeServer1.nativeElement,
      this.nodeServer2.nativeElement,
      this.nodeDb.nativeElement,
    ];
    gsap.set(nodes, { transformOrigin: '50% 50%' });

    const tl = gsap.timeline({ repeat: -1 });

    tl.to(this.nodeClient.nativeElement, { scale: 1.15, duration: 0.35, ease: 'power1.out' })
      .to(this.nodeClient.nativeElement, { scale: 1, duration: 0.35, ease: 'power1.in' })
      .to(this.lineClientLb.nativeElement, { opacity: 1, duration: 0.2 }, '<')
      .to(this.nodeLb.nativeElement, { scale: 1.15, duration: 0.35, ease: 'power1.out' }, '-=0.15')
      .to(this.nodeLb.nativeElement, { scale: 1, duration: 0.35, ease: 'power1.in' })
      .to(
        [this.lineLbServer1.nativeElement, this.lineLbServer2.nativeElement],
        { opacity: 1, duration: 0.2 },
        '<',
      )
      .to(
        [this.nodeServer1.nativeElement, this.nodeServer2.nativeElement],
        { scale: 1.15, duration: 0.35, ease: 'power1.out' },
        '-=0.15',
      )
      .to([this.nodeServer1.nativeElement, this.nodeServer2.nativeElement], {
        scale: 1,
        duration: 0.35,
        ease: 'power1.in',
      })
      .to(
        [this.lineServer1Db.nativeElement, this.lineServer2Db.nativeElement],
        { opacity: 1, duration: 0.2 },
        '<',
      )
      .to(this.nodeDb.nativeElement, { scale: 1.15, duration: 0.35, ease: 'power1.out' }, '-=0.15')
      .to(this.nodeDb.nativeElement, { scale: 1, duration: 0.35, ease: 'power1.in' })
      .to(
        [
          this.lineClientLb.nativeElement,
          this.lineLbServer1.nativeElement,
          this.lineLbServer2.nativeElement,
          this.lineServer1Db.nativeElement,
          this.lineServer2Db.nativeElement,
        ],
        { opacity: 0.35, duration: 0.4 },
        '+=0.2',
      );

    return tl;
  }
}
