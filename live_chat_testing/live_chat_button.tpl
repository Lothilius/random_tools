<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    % if environment == 'prod':
        <script type='text/javascript' src='https://c.la1-c2-phx.salesforceliveagent.com/content/g/js/38.0/deployment.js'></script>
        <script type='text/javascript'>
            //  Set User Name for Live Agent
            liveagent.setName('Martin Valenzuela');

            //  Setup Default Cases
            liveagent.addCustomDetail('ContactIdDetail', '0035000002KRFrRAAX');
            liveagent.addCustomDetail('AccountIdDetail', '0015000000cmCxXAAU');
            liveagent.addCustomDetail('CaseOrigin', 'Web');

            // below is replacement code per chuck
            liveagent.findOrCreate('Contact').map('Id', 'ContactIdDetail', true, true, false).saveToTranscript('ContactId');
            liveagent.findOrCreate('Account').map('Id', 'AccountIdDetail', true, true, false).saveToTranscript('AccountId');
            // end of replacement code per chuck

            liveagent.init('https://d.la1-c2-phx.salesforceliveagent.com/chat', '57250000000GmvK', '00D300000000zZB');
        </script>
    % else:
        <script type='text/javascript' src='https://c.la1-c1cs-phx.salesforceliveagent.com/content/g/js/39.0/deployment.js'></script>
        <script type='text/javascript'>
            //  Set User Name for Live Agent
            liveagent.setName('Martin Valenzuela');

            //  Setup Default Cases
            liveagent.addCustomDetail('ContactIdDetail', '0035000002KRFrRAAX');
            liveagent.addCustomDetail('AccountIdDetail', '0015000000cmCxXAAU');
            liveagent.addCustomDetail('CaseOrigin', 'Web');

            // below is replacement code per chuck
            liveagent.findOrCreate('Contact').map('Id', 'ContactIdDetail', true, true, false).saveToTranscript('ContactId');
            liveagent.findOrCreate('Account').map('Id', 'AccountIdDetail', true, true, false).saveToTranscript('AccountId');
            // end of replacement code per chuck

            liveagent.init('https://d.la3-c1cs-dfw.salesforceliveagent.com/chat', '57250000000GmvK', '00D3D0000000Shf');
        </script>
    % end
</head>
<body>
Hello {{environment}}
    <a id="liveagent_button_online_573500000008P6o" href="javascript://Chat" style="display: none;" onclick="liveagent.startChat('573500000008P6o')"><!-- Online Chat Content -->Let's Chat</a>
    <div id="liveagent_button_offline_573500000008P6o" style="display: none;"><!-- Offline Chat Content -->Let's not Chat</div>
    <script type="text/javascript">
        if (!window._laq) { window._laq = []; }
        window._laq.push(function(){liveagent.showWhenOnline('573500000008P6o', document.getElementById('liveagent_button_online_573500000008P6o'));
        liveagent.showWhenOffline('573500000008P6o', document.getElementById('liveagent_button_offline_573500000008P6o'));
        });
    </script>
</body>
</html>