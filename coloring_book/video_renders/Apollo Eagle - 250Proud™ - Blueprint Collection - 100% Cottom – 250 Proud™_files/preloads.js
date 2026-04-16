
    (function() {
      var cdnOrigin = "https://cdn.shopify.com";
      var scripts = ["/cdn/shopifycloud/checkout-web/assets/c1/polyfills.CgsWKOqO.js","/cdn/shopifycloud/checkout-web/assets/c1/app.KE0-95OJ.js","/cdn/shopifycloud/checkout-web/assets/c1/dist-vendor.DBR6g02j.js","/cdn/shopifycloud/checkout-web/assets/c1/browser.sAvoawcU.js","/cdn/shopifycloud/checkout-web/assets/c1/shop-pay-FullScreenBackground.CUfzz8_n.js","/cdn/shopifycloud/checkout-web/assets/c1/graphql-shared.Dt73nmDg.js","/cdn/shopifycloud/checkout-web/assets/c1/actions-shop-discount-offer.DVpxy7Jj.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-alternativePaymentCurrency.C7vFbqPs.js","/cdn/shopifycloud/checkout-web/assets/c1/utils-proposal.CEb0buGd.js","/cdn/shopifycloud/checkout-web/assets/c1/shop-pay-ButtonWithRegisterWebPixel.Bb6ujYnt.js","/cdn/shopifycloud/checkout-web/assets/c1/images-flag-icon.C_eXYJRt.js","/cdn/shopifycloud/checkout-web/assets/c1/images-payment-icon.BXeXx6hF.js","/cdn/shopifycloud/checkout-web/assets/c1/locale-en.0B7nEUPA.js","/cdn/shopifycloud/checkout-web/assets/c1/page-OnePage.BlKIdGR2.js","/cdn/shopifycloud/checkout-web/assets/c1/Captcha-PaymentButtons.BrMwWs6T.js","/cdn/shopifycloud/checkout-web/assets/c1/Menu-LocalPickup.D2YrsK3N.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-NoAddressLocation.DilR4CJt.js","/cdn/shopifycloud/checkout-web/assets/c1/shopPaySessionTokenStorage-Page.DzjUg09x.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-MarketsProDisclaimer.BIFM8Ivw.js","/cdn/shopifycloud/checkout-web/assets/c1/icons-OffsitePaymentFailed.DoXAgngx.js","/cdn/shopifycloud/checkout-web/assets/c1/icons-ShopPayLogo.Bfs14Fun.js","/cdn/shopifycloud/checkout-web/assets/c1/BuyWithPrimeChangeLink-VaultedPayment.2XIofisP.js","/cdn/shopifycloud/checkout-web/assets/c1/DeliveryMacros-ShippingGroupsSummaryLine.CU9QwXA7.js","/cdn/shopifycloud/checkout-web/assets/c1/MerchandisePreviewThumbnail-StackedMerchandisePreview.CMjBZmt9.js","/cdn/shopifycloud/checkout-web/assets/c1/Map-PickupPointCarrierLogo.BNqnC4zF.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks.B4JwyUGk.js","/cdn/shopifycloud/checkout-web/assets/c1/PostPurchaseShouldRender-AddDiscountButton.CDaZa9q-.js","/cdn/shopifycloud/checkout-web/assets/c1/graphql-RememberMeDescriptionText.CTg2_SQh.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-ShopPayOptInDisclaimer.wGi2lJhX.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-MobileOrderSummary.xi68P_-K.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-OrderEditVaultedDelivery.CZFwEBPK.js","/cdn/shopifycloud/checkout-web/assets/c1/captcha-SeparatePaymentsNotice.BW2aESrf.js","/cdn/shopifycloud/checkout-web/assets/c1/types-useHasOrdersFromMultipleShops.5_5TLVlA.js","/cdn/shopifycloud/checkout-web/assets/c1/StockProblems-StockProblemsLineItemList.DyyTicYx.js","/cdn/shopifycloud/checkout-web/assets/c1/redemption-useShopCashCheckoutEligibility.BcFDjXnG.js","/cdn/shopifycloud/checkout-web/assets/c1/negotiated-ShipmentBreakdown.CkPBl3nF.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-MerchandiseModal.D9nwZJ9z.js","/cdn/shopifycloud/checkout-web/assets/c1/utilities-shipping-options.B2lHBfDE.js","/cdn/shopifycloud/checkout-web/assets/c1/graphql-DutyOptions.D7pnv50h.js","/cdn/shopifycloud/checkout-web/assets/c1/DeliveryInstructionsFooter-ShippingMethodSelector.CDTqXu9J.js","/cdn/shopifycloud/checkout-web/assets/c1/hooks-SubscriptionPriceBreakdown.C9qdq8J0.js"];
      var styles = ["/cdn/shopifycloud/checkout-web/assets/c1/assets/app.fH9d1Lew.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/FullScreenBackground.-XSmsMDv.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ButtonWithRegisterWebPixel.BztvPw8A.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/OnePage.Di1yeo0T.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/LocalPickup.DmhmOh0D.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/AddDiscountButton.oEoBAbtG.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/MobileOrderSummary.Cko1fUoG.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/OrderEditVaultedDelivery.CSQKPDv7.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/NoAddressLocation.BrcQzLuH.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/DutyOptions.LcqrKXE1.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/VaultedPayment.OxMVm7u-.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PickupPointCarrierLogo.cbVP6Hp_.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Page.BYM12A8B.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/OffsitePaymentFailed.BxwwfmsJ.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/StackedMerchandisePreview.D6OuIVjc.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ShippingMethodSelector.B0hio2RO.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/SubscriptionPriceBreakdown.BSemv9tH.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useHasOrdersFromMultipleShops.D14orovx.css"];
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
  