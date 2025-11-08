/**
 * Settings component provides application configuration options.
 *
 * Allows users to configure notifications, preferences, and farm settings.
 *
 * @component
 * @returns {JSX.Element} The settings view
 */
import { useState, useCallback } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Separator } from "./ui/separator";
import { Badge } from "./ui/badge";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

interface NotificationSettings {
  /** Enable in-app notifications */
  inApp: boolean;
  /** Enable email notifications */
  email: boolean;
  /** Enable SMS notifications */
  sms: boolean;
  /** Enable push notifications */
  push: boolean;
}

export function Settings(): JSX.Element {
  const [notifications, setNotifications] = useState<NotificationSettings>({
    inApp: true,
    email: true,
    sms: false,
    push: true,
  });

  /**
   * Handles saving settings and shows success notification.
   */
  const handleSave = useCallback((): void => {
    toast.success("Settings saved successfully");
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2>Settings</h2>
        <p className="text-slate-600">Manage your farm settings and preferences</p>
      </div>

      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="farm">Farm</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="about">About</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card className="p-6">
            <h3 className="mb-6">Profile Settings</h3>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" defaultValue="John Doe" className="mt-2" />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    defaultValue="john@sunnydalefarm.com"
                    className="mt-2"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" defaultValue="+1 (555) 123-4567" className="mt-2" />
                </div>
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Select defaultValue="owner">
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="owner">Farm Owner</SelectItem>
                      <SelectItem value="manager">Farm Manager</SelectItem>
                      <SelectItem value="worker">Farm Worker</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator />

              <div className="flex justify-end gap-2">
                <Button 
                  variant="outline"
                  onClick={() => toast.info("Changes discarded")}
                >
                  Cancel
                </Button>
                <Button onClick={handleSave} className="bg-emerald-600 hover:bg-emerald-700">
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Farm Tab */}
        <TabsContent value="farm">
          <Card className="p-6">
            <h3 className="mb-6">Farm Settings</h3>
            <div className="space-y-6">
              <div>
                <Label htmlFor="farmName">Farm Name</Label>
                <Input id="farmName" defaultValue="Sunnydale Farm" className="mt-2" />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input id="location" defaultValue="Salinas Valley, CA" className="mt-2" />
                </div>
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select defaultValue="pst">
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pst">Pacific Time (PST)</SelectItem>
                      <SelectItem value="mst">Mountain Time (MST)</SelectItem>
                      <SelectItem value="cst">Central Time (CST)</SelectItem>
                      <SelectItem value="est">Eastern Time (EST)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="crops">Primary Crops</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge variant="outline">Strawberry</Badge>
                  <Badge variant="outline">Lettuce</Badge>
                  <Badge variant="outline">Tomato</Badge>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => toast.info("Add crop functionality coming soon")}
                  >
                    + Add Crop
                  </Button>
                </div>
              </div>

              <div>
                <Label>Total Farm Area</Label>
                <Input defaultValue="45 hectares" className="mt-2" />
              </div>

              <Separator />

              <div className="flex justify-end gap-2">
                <Button 
                  variant="outline"
                  onClick={() => toast.info("Changes discarded")}
                >
                  Cancel
                </Button>
                <Button onClick={handleSave} className="bg-emerald-600 hover:bg-emerald-700">
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card className="p-6">
            <h3 className="mb-6">Notification Preferences</h3>
            <div className="space-y-6">
              <div>
                <h4 className="mb-4">Alert Channels</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="in-app">In-App Notifications</Label>
                      <p className="text-slate-500">Receive alerts within the application</p>
                    </div>
                    <Switch
                      id="in-app"
                      checked={notifications.inApp}
                      onCheckedChange={(checked) =>
                        setNotifications({ ...notifications, inApp: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="email">Email Notifications</Label>
                      <p className="text-slate-500">Send alerts to your email address</p>
                    </div>
                    <Switch
                      id="email"
                      checked={notifications.email}
                      onCheckedChange={(checked) =>
                        setNotifications({ ...notifications, email: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="sms">SMS Notifications</Label>
                      <p className="text-slate-500">Receive text messages for critical alerts</p>
                    </div>
                    <Switch
                      id="sms"
                      checked={notifications.sms}
                      onCheckedChange={(checked) =>
                        setNotifications({ ...notifications, sms: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="push">Push Notifications</Label>
                      <p className="text-slate-500">Mobile push notifications</p>
                    </div>
                    <Switch
                      id="push"
                      checked={notifications.push}
                      onCheckedChange={(checked) =>
                        setNotifications({ ...notifications, push: checked })
                      }
                    />
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="mb-4">Quiet Hours</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>From</Label>
                    <Input type="time" defaultValue="22:00" className="mt-2" />
                  </div>
                  <div>
                    <Label>To</Label>
                    <Input type="time" defaultValue="08:00" className="mt-2" />
                  </div>
                </div>
                <p className="text-slate-500 mt-2">
                  Non-critical notifications will be silenced during these hours
                </p>
              </div>

              <Separator />

              <div className="flex justify-end gap-2">
                <Button 
                  variant="outline"
                  onClick={() => toast.info("Changes discarded")}
                >
                  Cancel
                </Button>
                <Button onClick={handleSave} className="bg-emerald-600 hover:bg-emerald-700">
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* About Tab */}
        <TabsContent value="about">
          <Card className="p-6">
            <h3 className="mb-6">About Growgent</h3>
            <div className="space-y-6">
              <div>
                <Label>Version</Label>
                <p className="text-slate-900 mt-1">1.0.0-beta</p>
              </div>

              <div>
                <Label>License</Label>
                <p className="text-slate-900 mt-1">AGPL v3 (Open Source)</p>
              </div>

              <div>
                <Label>Description</Label>
                <p className="text-slate-700 mt-1">
                  Growgent is an open-source agentic platform for fire-adaptive irrigation
                  management. Built to solve California agriculture's critical challenges during
                  drought and wildfire seasons.
                </p>
              </div>

              <Separator />

              <div className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => toast.info("Opening documentation...")}
                >
                  📚 View Documentation
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => toast.info("Opening GitHub repository...")}
                >
                  🔗 GitHub Repository
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => toast.info("Opening support portal...")}
                >
                  💬 Get Support
                </Button>
              </div>

              <Separator />

              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-slate-700">
                  <strong>Note:</strong> Growgent is not designed for collecting PII or securing
                  sensitive data. Please consult your legal and security teams before deploying in
                  production.
                </p>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
