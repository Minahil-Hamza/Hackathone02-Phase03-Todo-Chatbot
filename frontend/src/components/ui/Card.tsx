"use client";

import { HTMLAttributes, forwardRef } from "react";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "bordered";
  padding?: "none" | "sm" | "md" | "lg";
}

/**
 * Card component for containing content with consistent styling
 *
 * @example
 * <Card variant="elevated" padding="md">
 *   <h3>Card Title</h3>
 *   <p>Card content</p>
 * </Card>
 */
const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = "default",
      padding = "md",
      className = "",
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = "rounded-lg transition-all duration-200";

    const variantStyles = {
      default:
        "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700",
      elevated:
        "bg-white dark:bg-slate-800 shadow-md hover:shadow-lg",
      bordered:
        "bg-white dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-600",
    };

    const paddingStyles = {
      none: "",
      sm: "p-3",
      md: "p-4",
      lg: "p-6",
    };

    return (
      <div
        ref={ref}
        className={`${baseStyles} ${variantStyles[variant]} ${paddingStyles[padding]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";

export default Card;
