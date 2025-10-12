import UIKit
import Capacitor

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        
        // Configure any additional settings for IELTS AI Prep
        configureAppearance()
        
        return true
    }
    
    private func configureAppearance() {
        // Set app appearance and branding
        if #available(iOS 13.0, *) {
            // Configure navigation bar appearance
            let navBarAppearance = UINavigationBarAppearance()
            navBarAppearance.backgroundColor = UIColor(red: 67/255, green: 97/255, blue: 238/255, alpha: 1.0)
            navBarAppearance.titleTextAttributes = [.foregroundColor: UIColor.white]
            UINavigationBar.appearance().standardAppearance = navBarAppearance
            UINavigationBar.appearance().scrollEdgeAppearance = navBarAppearance
        }
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        // Handle deep links and QR code authentication
        if url.scheme == "ieltsaiprep" {
            // Handle custom scheme for QR code authentication
            let webURL = "https://ieltsaiprep.com" + url.path
            var urlString = webURL
            
            if let query = url.query {
                urlString += "?" + query
            }
            
            // Load the URL in the WebView
            DispatchQueue.main.async {
                if let webView = CAPBridge.getLastBridge()?.webView {
                    webView.load(URLRequest(url: URL(string: urlString)!))
                }
            }
        }
        
        // Make sure to keep this call for Capacitor functionality
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        // Called when the app was launched with an activity, including Universal Links
        // Handle universal links for QR code authentication
        if userActivity.activityType == NSUserActivityTypeBrowsingWeb,
           let url = userActivity.webpageURL,
           url.host?.contains("ieltsaiprep.com") == true {
            
            // Load the URL in the WebView for seamless QR code authentication
            DispatchQueue.main.async {
                if let webView = CAPBridge.getLastBridge()?.webView {
                    webView.load(URLRequest(url: url))
                }
            }
            
            return true
        }
        
        // Make sure to keep this call for Capacitor functionality
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }
}