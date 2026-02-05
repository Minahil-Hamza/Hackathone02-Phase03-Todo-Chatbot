"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "destructive";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

/**
 * Button component with multiple variants and accessibility features
 *
 * @example
 * <Button variant="primary" onClick={handleClick}>Click me</Button>
 */
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      isLoading = false,
      disabled,
      className = "",
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95";

    const variantStyles = {
      primary:
        "bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500",
      secondary:
        "bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 focus:ring-indigo-500 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-gray-200 dark:border-slate-600",
      ghost:
        "hover:bg-gray-100 text-gray-600 focus:ring-indigo-500 dark:hover:bg-slate-800 dark:text-gray-300",
      destructive:
        "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500",
    };

    const sizeStyles = {
      sm: "text-xs px-3 py-1.5 rounded-md gap-1.5",
      md: "text-sm px-4 py-2 rounded-lg gap-2",
      lg: "text-base px-6 py-3 rounded-lg gap-2",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <span className="loading-dots flex gap-1" aria-label="Loading">
              <span className="loading-dot w-1.5 h-1.5 bg-current rounded-full"></span>
              <span className="loading-dot w-1.5 h-1.5 bg-current rounded-full"></span>
              <span className="loading-dot w-1.5 h-1.5 bg-current rounded-full"></span>
            </span>
            <span className="sr-only">Loading...</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
