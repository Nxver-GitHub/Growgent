import { Toaster as Sonner, ToasterProps } from "sonner";

const Toaster = ({ ...props }: ToasterProps) => {
  // For Vite/React, we'll use system theme detection
  // If you want theme switching, integrate with your theme provider
  const theme = "system";

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--popover-foreground)",
          "--normal-border": "var(--border)",
        } as React.CSSProperties
      }
      position="top-right"
      toastOptions={{
        style: {
          zIndex: 110, // Above dialogs
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
