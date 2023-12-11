<?php if (!defined('QUFORM_ROOT')) exit; ?><html>
<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td valign="top" style="padding: 25px;"><table width="600" cellpadding="0" cellspacing="0" border="0" style="font: 14px Helvetica, Arial, sans-serif;">
            <tr>
                <td valign="top" style="font-family: Helvetica, Arial, sans-serif; font-size: 25px; font-weight: bold; color: #282828; padding-bottom: 10px;"><?php echo Quform::escape($mailer->Subject); ?></td>
            </tr>
            <tr>
                <td valign="top">Just to let you know we received your message and we will get back to you as soon as possible.</td>
            </tr>
        </table></td>
    </tr>
</table>
</body>
</html>