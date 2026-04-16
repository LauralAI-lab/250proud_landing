
    (function() {
      var cdnOrigin = "https://cdn.shopify.com";
      var scripts = ["/cdn/shopifycloud/checkout-web/assets/c1/polyfills.CgsWKOqO.js","/cdn/shopifycloud/checkout-web/assets/c1/app.DHO1idO4.js","/cdn/shopifycloud/checkout-web/assets/c1/dist-vendor.BXQacVoS.js","/cdn/shopifycloud/checkout-web/assets/c1/browser.BjFwX2mU.js","/cdn/shopifycloud/checkout-web/assets/c1/shop-pay-useUnauthenticatedErrorModal.C7WfrQjA.js","/cdn/shopifycloud/checkout-web/assets/c1/graphql-shared.-QAFmlnX.js","/cdn/shopifycloud/checkout-web/assets/c1/actions-shop-discount-offer.stEN-UVv.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-alternativePaymentCurrency.2V7J7kAW.js","/cdn/shopifycloud/checkout-web/assets/c1/utils-proposal.CF1rkWUs.js","/cdn/shopifycloud/checkout-web/assets/c1/extensibility-useReplaceShopPayInHistory.Ce4s3eBj.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-FullScreenBackground.DngYUdtj.js","/cdn/shopifycloud/checkout-web/assets/c1/images-flag-icon.C_eXYJRt.js","/cdn/shopifycloud/checkout-web/assets/c1/images-payment-icon.BXeXx6hF.js","/cdn/shopifycloud/checkout-web/assets/c1/locale-en.CpDj_pEh.js","/cdn/shopifycloud/checkout-web/assets/c1/page-OnePage.D7CtPQhf.js","/cdn/shopifycloud/checkout-web/assets/c1/Captcha-MarketsProDisclaimer.il0HaMov.js","/cdn/shopifycloud/checkout-web/assets/c1/Menu-LocalPickup.p1vmj1PY.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-useEditorShopPayNavigation.C_-87ccV.js","/cdn/shopifycloud/checkout-web/assets/c1/adapter-useForceShopPayUrl.B7H4WMAN.js","/cdn/shopifycloud/checkout-web/assets/c1/icons-ShopPayLogo.Depnqwkq.js","/cdn/shopifycloud/checkout-web/assets/c1/BuyWithPrimeChangeLink-VaultedPayment.BvOAmpxf.js","/cdn/shopifycloud/checkout-web/assets/c1/DeliveryMacros-ShippingGroupsSummaryLine.B3BUtwny.js","/cdn/shopifycloud/checkout-web/assets/c1/MerchandisePreviewThumbnail-StackedMerchandisePreview.Djnp-05q.js","/cdn/shopifycloud/checkout-web/assets/c1/Map-PickupPointCarrierLogo.ZlHM8CWx.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks.BhKaJiLc.js","/cdn/shopifycloud/checkout-web/assets/c1/PostPurchaseShouldRender-LocalizationExtensionField.B31DU0me.js","/cdn/shopifycloud/checkout-web/assets/c1/graphql-useShowShopPayOptin.BcFSVaP0.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-ShopPayOptInDisclaimer.Dm3mo_OW.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-RememberMeDescriptionText.BY0ol6zc.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-MobileOrderSummary.BaRYidg8.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-OrderEditVaultedDelivery.CAvB7shF.js","/cdn/shopifycloud/checkout-web/assets/c1/captcha-SeparatePaymentsNotice.Ce6tLyZ_.js","/cdn/shopifycloud/checkout-web/assets/c1/StockProblems-StockProblemsLineItemList.BJdZY3Ej.js","/cdn/shopifycloud/checkout-web/assets/c1/component-ShopPayVerificationSwitch.Bpbncjxs.js","/cdn/shopifycloud/checkout-web/assets/c1/shop-js-index.CxJaaA1r.js","/cdn/shopifycloud/checkout-web/assets/c1/esm-browser-v4.BKrj-4V8.js","/cdn/shopifycloud/checkout-web/assets/c1/redemption-useShopCashCheckoutEligibility.hACJKbLJ.js","/cdn/shopifycloud/checkout-web/assets/c1/negotiated-ShipmentBreakdown.DcX-fb6F.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-MerchandiseModal.Cv2oARTw.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-shipping-options.Dd13ODFo.js","/cdn/shopifycloud/checkout-web/assets/c1/graphql-DutyOptions.C82RWLel.js","/cdn/shopifycloud/checkout-web/assets/c1/DeliveryInstructionsFooter-ShippingMethodSelector.D4PYSS2m.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-SubscriptionPriceBreakdown.DuPIW1ec.js"];
      var styles = ["/cdn/shopifycloud/checkout-web/assets/c1/assets/app.fH9d1Lew.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useUnauthenticatedErrorModal.CCVI6dbY.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/FullScreenBackground._EbZwryl.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/OnePage.Di1yeo0T.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/LocalPickup.DmhmOh0D.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/LocalizationExtensionField.oEoBAbtG.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/MobileOrderSummary.Cko1fUoG.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/OrderEditVaultedDelivery.CSQKPDv7.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ShopPayVerificationSwitch.WW3cs_z5.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useEditorShopPayNavigation.BrcQzLuH.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/DutyOptions.LcqrKXE1.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/VaultedPayment.OxMVm7u-.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PickupPointCarrierLogo.cbVP6Hp_.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/StackedMerchandisePreview.D6OuIVjc.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ShippingMethodSelector.B0hio2RO.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/SubscriptionPriceBreakdown.BSemv9tH.css"];
      var fontPreconnectUrls = [];
      var fontPrefetchUrls = [];
      var imgPrefetchUrls = [];

      function preconnect(url, callback) {
        var link = document.createElement('link');
        link.rel = 'dns-prefetch preconnect';
        link.href = url;
        link.crossOrigin = '';
        link.onload = link.onerror = callback;
        document.head.appendChild(link);
      }

      function preconnectAssets() {
        var resources = [cdnOrigin].concat(fontPreconnectUrls);
        var index = 0;
        (function next() {
          var res = resources[index++];
          if (res) preconnect(res, next);
        })();
      }

      function prefetch(url, as, callback) {
        var link = document.createElement('link');
        if (link.relList.supports('prefetch')) {
          link.rel = 'prefetch';
          link.fetchPriority = 'low';
          link.as = as;
          if (as === 'font') link.type = 'font/woff2';
          link.href = url;
          link.crossOrigin = '';
          link.onload = link.onerror = callback;
          document.head.appendChild(link);
        } else {
          var xhr = new XMLHttpRequest();
          xhr.open('GET', url, true);
          xhr.onloadend = callback;
          xhr.send();
        }
      }

      function prefetchAssets() {
        var resources = [].concat(
          scripts.map(function(url) { return [url, 'script']; }),
          styles.map(function(url) { return [url, 'style']; }),
          fontPrefetchUrls.map(function(url) { return [url, 'font']; }),
          imgPrefetchUrls.map(function(url) { return [url, 'image']; })
        );
        var index = 0;
        function run() {
          var res = resources[index++];
          if (res) prefetch(res[0], res[1], next);
        }
        var next = (self.requestIdleCallback || setTimeout).bind(self, run);
        next();
      }

      function onLoaded() {
        try {
          if (parseFloat(navigator.connection.effectiveType) > 2 && !navigator.connection.saveData) {
            preconnectAssets();
            prefetchAssets();
          }
        } catch (e) {}
      }

      if (document.readyState === 'complete') {
        onLoaded();
      } else {
        addEventListener('load', onLoaded);
      }
    })();
  