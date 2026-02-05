"use client";

interface SkeletonProps {
  className?: string;
}

export default function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`skeleton ${className}`} />;
}

export function MessageSkeleton() {
  return (
    <div className="flex gap-4 animate-fade-in">
      <div className="skeleton w-8 h-8 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="skeleton w-16 h-3 rounded" />
        <div className="card p-4 space-y-2">
          <div className="skeleton w-full h-4 rounded" />
          <div className="skeleton w-4/5 h-4 rounded" />
          <div className="skeleton w-2/3 h-4 rounded" />
        </div>
        <div className="skeleton w-12 h-3 rounded" />
      </div>
    </div>
  );
}

export function TaskCardSkeleton() {
  return (
    <div className="card p-3 flex items-start gap-3">
      <div className="skeleton w-5 h-5 rounded-md flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="skeleton w-full h-4 rounded" />
        <div className="skeleton w-2/3 h-3 rounded" />
      </div>
    </div>
  );
}
